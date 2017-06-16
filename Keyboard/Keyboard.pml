<?xml version="1.0" encoding="UTF-8" ?>
<Package name="Keyboard" format_version="4">
    <Manifest src="manifest.xml" />
    <BehaviorDescriptions>
        <BehaviorDescription name="behavior" src="behavior_1" xar="behavior.xar" />
    </BehaviorDescriptions>
    <Dialogs>
        <Dialog name="keyboard" src="keyboard/keyboard.dlg" />
    </Dialogs>
    <Resources>
        <File name="pepper" src="html/css/pepper.css" />
        <File name="logo" src="html/img/logo.png" />
        <File name="pepper" src="html/img/pepper.png" />
        <File name="index" src="html/index.html" />
        <File name="app_script" src="html/js/app_script.js" />
        <File name="jquery-2.1.4.min" src="html/js/jquery-2.1.4.min.js" />
        <File name="numpad" src="html/js/numpad.js" />
        <File name="qimessaging_helper" src="html/js/qimessaging_helper.js" />
        <File name="main" src="main.py" />
    </Resources>
    <Topics>
        <Topic name="keyboard_enu" src="keyboard/keyboard_enu.top" topicName="keyboard" language="en_US" />
    </Topics>
    <IgnoredPaths />
    <Translations auto-fill="en_US">
        <Translation name="translation_en_US" src="translations/translation_en_US.ts" language="en_US" />
    </Translations>
</Package>
