#!/usr/bin/env python3
"""Runs Flatpak operations for Stash through libflatpak and reports progress as JSON lines, so the window can show real percentages and download speed. A separate process keeps GLib's main loop away from Qt's threads.

  flatpak_helper.py [--user] list                  installed apps
  flatpak_helper.py [--user] updates               apps and runtimes with an update
  flatpak_helper.py [--user] unused                runtimes nothing uses any more
  flatpak_helper.py [--user] install APP_ID
  flatpak_helper.py [--user] remove APP_ID
  flatpak_helper.py [--user] update APP_ID [APP_ID ...]
  flatpak_helper.py [--user] update-all
  flatpak_helper.py [--user] prune                 remove unused runtimes

System installation by default (Flatpak's polkit rules allow the active local user); --user is for tests. SIGTERM or SIGINT cancels a running transaction.
"""
import json
import re
import signal
import sys

import gi
gi.require_version("Flatpak", "1.0")
from gi.repository import Flatpak, Gio, GLib

REMOTE = "flathub"
APP_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{2,254}$")
CANCEL = Gio.Cancellable()


def emit(**fields):
    """Print a JSON object and flush stdout."""
    print(json.dumps(fields), flush=True)


def on_signal(signum, frame):
    """Cancel the current transaction on SIGTERM or SIGINT."""
    CANCEL.cancel()


def installation(user):
    """Return a user or system Flatpak.Installation."""
    if user:
        return Flatpak.Installation.new_user(None)
    return Flatpak.Installation.new_system(None)


def app_entry(ref):
    """Build a dict describing an installed app ref."""
    return {
        "id": ref.get_name(),
        "name": ref.get_appdata_name() or ref.get_name(),
        "version": ref.get_appdata_version() or "",
        "summary": ref.get_appdata_summary() or "",
        "installed_size": ref.get_installed_size(),
        "origin": ref.get_origin() or "",
        "branch": ref.get_branch() or "",
        "eol": bool(ref.get_eol() or ref.get_eol_rebase()),
    }


def cmd_list(inst):
    """List all installed apps."""
    refs = inst.list_installed_refs_by_kind(Flatpak.RefKind.APP, None)
    emit(event="list", apps=sorted((app_entry(r) for r in refs), key=lambda a: a["name"].lower()))


def cmd_updates(inst):
    """List installed refs that have an update available."""
    refs = inst.list_installed_refs_for_update(None)
    emit(
        event="updates",
        refs=[
            {
                "id": r.get_name(),
                "kind": "app" if r.get_kind() == Flatpak.RefKind.APP else "runtime",
                "ref": r.format_ref(),
            }
            for r in refs
        ],
    )


def cmd_unused(inst):
    """List unused runtimes."""
    refs = inst.list_unused_refs(None, None)
    emit(event="unused", count=len(refs), size=sum(r.get_installed_size() for r in refs))


def find_remote_ref(inst, app_id):
    """Find the remote ref string for *app_id* on REMOTE.

    Tries branch "stable" first, then falls back to None (default).
    """
    try:
        return inst.fetch_remote_ref_sync(
            REMOTE, Flatpak.RefKind.APP, app_id,
            Flatpak.get_default_arch(), "stable", None,
        ).format_ref()
    except GLib.Error:
        pass
    ref = inst.fetch_remote_ref_sync(
        REMOTE, Flatpak.RefKind.APP, app_id,
        Flatpak.get_default_arch(), None, None,
    )
    return ref.format_ref()


def installed_ref(inst, app_id):
    """Return the formatted ref string of an installed *app_id*."""
    for r in inst.list_installed_refs_by_kind(Flatpak.RefKind.APP, None):
        if r.get_name() == app_id:
            return r.format_ref()
    raise ValueError(f"{app_id} is not installed")


def run_transaction(inst, build, targets):
    """Run a Flatpak transaction and emit JSON progress events.

    *build* is called with the transaction object to add operations.
    *targets* is a set of app ids whose failure is fatal.
    """
    t = Flatpak.Transaction.new_for_installation(inst, None)
    t.set_no_interaction(True)
    build(t)

    state = {"index": 0}

    def new_operation(tr, op, progress):
        """Emit metadata for a newly queued operation."""
        state["index"] += 1
        ref = op.get_ref()
        emit(
            event="operation",
            index=state["index"],
            total=len(tr.get_operations()),
            type=op.get_operation_type().value_nick,
            ref=ref,
            name=ref.split("/")[1] if "/" in ref else ref,
            download_size=op.get_download_size(),
            installed_size=op.get_installed_size(),
        )
        progress.set_update_frequency(400)

        def changed(p):
            """Emit a progress update."""
            if CANCEL.is_cancelled():
                return True
            emit(
                event="progress",
                index=state["index"],
                percent=p.get_progress(),
                status=p.get_status() or "",
                bytes=p.get_bytes_transferred(),
            )
            return True

        progress.connect("changed", changed)

    def operation_done(tr, op, commit, result):
        """Emit that an operation completed."""
        emit(event="operation-done", ref=op.get_ref())

    def operation_error(tr, op, error, details):
        """Handle a per-operation error; return True to continue."""
        ref = op.get_ref()
        name = ref.split("/")[1] if "/" in ref else ref
        fatal = name in targets
        emit(
            event="error" if fatal else "warning",
            ref=ref,
            message=error.message,
        )
        return not fatal

    t.connect("new-operation", new_operation)
    t.connect("operation-done", operation_done)
    t.connect("operation-error", operation_error)

    try:
        t.run(CANCEL)
    except GLib.Error as error:
        if CANCEL.is_cancelled():
            emit(event="cancelled")
            return 3
        emit(event="failed", message=error.message)
        return 1

    emit(event="finished")
    return 0


def main(argv):
    """Parse arguments and dispatch to the requested command."""
    args = list(argv[1:])
    user = False
    if args and args[0] == "--user":
        user = True
        args = args[1:]

    if not args:
        print(__doc__, file=sys.stderr)
        return 2

    command, rest = args[0], args[1:]

    signal.signal(signal.SIGTERM, on_signal)
    signal.signal(signal.SIGINT, on_signal)

    for app_id in rest:
        if not APP_ID.match(app_id):
            emit(event="failed", message=f"bad app id: {app_id}")
            return 2

    try:
        inst = installation(user)

        if command == "list":
            cmd_list(inst)
            return 0

        if command == "updates":
            cmd_updates(inst)
            return 0

        if command == "unused":
            cmd_unused(inst)
            return 0

        if command == "install" and len(rest) == 1:
            ref = find_remote_ref(inst, rest[0])
            return run_transaction(
                inst, lambda t: t.add_install(REMOTE, ref, None), {rest[0]}
            )

        if command == "remove" and len(rest) == 1:
            ref = installed_ref(inst, rest[0])
            return run_transaction(
                inst, lambda t: t.add_uninstall(ref), {rest[0]}
            )

        if command == "update" and rest:
            refs = [installed_ref(inst, a) for a in rest]
            return run_transaction(
                inst,
                lambda t: [t.add_update(r, None, None) for r in refs],
                set(rest),
            )

        if command == "update-all":
            refs = [r.format_ref() for r in inst.list_installed_refs_for_update(None)]
            if not refs:
                emit(event="finished")
                return 0
            return run_transaction(
                inst,
                lambda t: [t.add_update(r, None, None) for r in refs],
                set(),
            )

        if command == "prune":
            refs = [r.format_ref() for r in inst.list_unused_refs(None, None)]
            if not refs:
                emit(event="finished")
                return 0
            return run_transaction(
                inst,
                lambda t: [t.add_uninstall(r) for r in refs],
                set(),
            )

        print(__doc__, file=sys.stderr)
        return 2

    except (GLib.Error, ValueError) as error:
        emit(event="failed", message=getattr(error, "message", None) or str(error))
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
