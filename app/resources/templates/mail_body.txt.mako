Описание проблемы: ${ request.description }
ФИО: ${ message.sender.username }
E-mail: ${ ", ".join(user.emails) if user.emails else "-"}
Номер мобильного телефона: ${ message.sender.ad_login }
Компания: ${ user.company }
Должность: ${ user.company_position }
Отдел: ${ user.department }
Название клиентской платформы: ${ platform }
% if platform in (client_platform_enum.IOS, client_platform_enum.ANDROID):
Имя бренда производителя девайса: ${ message.sender.device.manufacturer }
Модель девайса: ${ message.sender.device.device_name }
ОС девайса + версия операционной системы: ${ message.sender.device.os }
% elif platform == client_platform_enum.WEB:
Версия браузера: ${ message.sender.device.device_name }
ОС ПК + версия операционной системы: ${ message.sender.device.os }
% elif platform == client_platform_enum.DESKTOP:
ОС ПК + версия операционной системы: ${ message.sender.device.os }
% endif
Версия приложения ${ app_name }: ${ message.sender.device.app_version }
Имя сервера: ${ host }
Приложенные файлы: ${ ", ".join(request.attachments_names) if request.attachments_names else "-" }
