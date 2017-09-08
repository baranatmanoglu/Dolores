<?xml version="1.0" encoding="UTF-8" ?>
<Package name="AuthenticationLauncher" format_version="4">
    <Manifest src="manifest.xml" />
    <BehaviorDescriptions>
        <BehaviorDescription name="behavior" src="behavior_1" xar="behavior.xar" />
    </BehaviorDescriptions>
    <Dialogs>
        <Dialog name="authentication" src="authentication/authentication.dlg" />
    </Dialogs>
    <Resources>
        <File name="index" src="html/index.html" />
        <File name="jquery-2.1.4.min" src="html/js/jquery-2.1.4.min.js" />
        <File name="main" src="html/js/main.js" />
        <File name="qimessaging_helper" src="html/js/qimessaging_helper.js" />
        <File name="main" src="main.py" />
        <File name="main" src="html/css/main.css" />
        <File name="bg" src="html/img/bg.png" />
        <File name="buttonsBg+" src="html/img/buttonsBg+.png" />
        <File name="buttonsBg" src="html/img/buttonsBg.png" />
        <File name="card" src="html/img/card.png" />
        <File name="leftArrow" src="html/img/leftArrow.png" />
        <File name="logo" src="html/img/logo.png" />
        <File name="qr" src="html/img/qr.png" />
        <File name="rightArrow" src="html/img/rightArrow.png" />
        <File name="sound" src="html/img/sound.png" />
        <File name="type" src="html/img/type.png" />
        <File name="pepper" src="html/css/pepper.css" />
    </Resources>
    <Topics>
        <Topic name="authentication_enu" src="authentication/authentication_enu.top" topicName="authentication" language="en_US" />
    </Topics>
    <IgnoredPaths />
    <Translations auto-fill="en_US">
        <Translation name="translation_en_US" src="translations/translation_en_US.ts" language="en_US" />
    </Translations>
</Package>
