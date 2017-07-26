<?xml version="1.0" encoding="UTF-8" ?>
<Package name="GuideApp" format_version="4">
    <Manifest src="manifest.xml" />
    <BehaviorDescriptions>
        <BehaviorDescription name="behavior" src="behavior_1" xar="behavior.xar" />
    </BehaviorDescriptions>
    <Dialogs>
        <Dialog name="guidedialog" src="guidedialog/guidedialog.dlg" />
    </Dialogs>
    <Resources>
        <File name="pepper" src="html/css/pepper.css" />
        <File name="feet" src="html/images/feet.jpg" />
        <File name="pepper-blue" src="html/images/pepper-blue.jpg" />
        <File name="pepper-green" src="html/images/pepper-green.jpg" />
        <File name="pepper-red" src="html/images/pepper-red.jpg" />
        <File name="index" src="html/index.html" />
        <File name="jquery-2.1.4.min" src="html/js/jquery-2.1.4.min.js" />
        <File name="main" src="html/js/main.js" />
        <File name="qimessaging_helper" src="html/js/qimessaging_helper.js" />
        <File name="main" src="main.py" />
    </Resources>
    <Topics>
        <Topic name="guidedialog_enu" src="guidedialog/guidedialog_enu.top" topicName="guidedialog" language="en_US" />
    </Topics>
    <IgnoredPaths />
    <Translations auto-fill="en_US">
        <Translation name="translation_en_US" src="translations/translation_en_US.ts" language="en_US" />
    </Translations>
</Package>
