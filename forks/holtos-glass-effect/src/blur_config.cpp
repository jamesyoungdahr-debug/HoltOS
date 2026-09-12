/*
    SPDX-FileCopyrightText: 2010 Fredrik Höglund <fredrik@kde.org>

    SPDX-License-Identifier: GPL-2.0-or-later
*/
#include "blur_config.h"

// KWIN_CONFIG comes from config-kwin.h in-tree; out of tree the config file is simply kwinrc.
#define KWIN_CONFIG "kwinrc"

// KConfigSkeleton
#include "blurconfig.h"

#include <KPluginFactory>
#include <kwineffects_interface.h>

namespace KWin
{

// Inside the namespace: the macro pastes "Factory" onto the class name to
// declare the factory class, which cannot take a qualified name.
K_PLUGIN_CLASS(BlurEffectConfig)

BlurEffectConfig::BlurEffectConfig(QObject *parent, const KPluginMetaData &data)
    : KCModule(parent, data)
{
    ui.setupUi(widget());
    BlurConfig::instance(KWIN_CONFIG);
    addConfig(BlurConfig::self(), widget());
}

BlurEffectConfig::~BlurEffectConfig()
{
}

void BlurEffectConfig::save()
{
    KCModule::save();

    OrgKdeKwinEffectsInterface interface(QStringLiteral("org.kde.KWin"),
                                         QStringLiteral("/Effects"),
                                         QDBusConnection::sessionBus());
    interface.reconfigureEffect(QStringLiteral("holtosglass"));
}

} // namespace KWin

#include "blur_config.moc"

#include "moc_blur_config.cpp"
