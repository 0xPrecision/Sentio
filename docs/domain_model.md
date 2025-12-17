# Sentio Domain Model

## 1. Product overview

Sentio — это multi-tenant SaaS-система для онлайн-записи на услуги с Telegram-ботом в качестве 
основного клиентского интерфейса. Каждый бизнес (барбершоп, салон и т.п.) регистрируется 
как отдельный tenant и управляет своими локациями, мастерами, услугами и расписанием через админ-панель. 
Клиенты взаимодействуют только с Telegram-ботом: выбирают компанию, услугу, мастера 
и бронируют доступные слоты. Система отвечает за изоляцию данных между tenant’ами, 
генерацию свободных слотов, проверку бизнес-правил и отправку уведомлений мастерам и клиентам.


## 2. Actors (Roles)

### 2.1 Tenant owner (Admin)

Администратор (владелец бизнеса/доверенное лицо). 
Это пользовательский аккаунт, у которого есть роль для конкретного tenant (бизнеса). 
Может настраивать права доступа и управлять расписанием, услугами и салоном.

### 2.2 Staff member

Мастер (работник салона). 
Может просматривать и настраивать личное расписание, если есть разрешение от админа.

### 2.3 Customer

Пользователь приложения. 
Может выбрать компанию из каталога, выбрать услугу, забронировать время и отменить/перенести бронь, 
связаться с мастером. Имеет личный кабинет.

### 2.4 Sentio system

Система управления бизнесами. 
Следит за сепарацией компаний, проверяет права доступа, валидирует данные, генерирует слоты и
отправляет уведомления.


## 3. Entities & Relationships

### 3.1 Tenant

- **Description:**
    Представляет бизнес (барбершоп, салон и т.д.), использующий Sentio.

- **Key fields:**
  - id
  - name
  - contact_email
  - phone (optional)
  - plan
  - slug
  - timezone
  - settings_json
  - is_active (flag)
  - created_at, updated_at

- **Relations:**
  - has many TenantCustomers
  - has many Locations
  - has many StaffMembers
  - has many TenantUsers
  - has many Services
  - has many Bookings (через Locations)

### 3.2 Location

- **Description:**
    Физическое место, в котором предоставляются услуги бизнеса (tenant'а).

- **Key fields:**
  - id
  - tenant_id
  - name
  - address
  - description
  - is_default
  - is_active (flag)
  - created_at, updated_at
  
- **Relations:**
  - belongs to Tenant
  - has many StaffMembers
  - has many TenantUsers (optional)
  - has many Services (optional) 
  - has many Bookings (через StaffMembers)

### 3.3 User

- **Description:**
    Абстрактный аккаунт, содержащий в себе контактную информацию сотрудника бизнеса.

- **Key fields:**
  - id
  - telegram_id
  - full_name
  - phone (optional)
  - email
  - avatar_url
  - is_active (flag)
  - created_at, updated_at

- **Relations:**
  - has many StaffMembers
  - has many TenantUsers

### 3.4 TenantUser

- **Description:**
    Представитель бизнеса, который использует Sentio как платформу для бронирования.

- **Key fields:**
  - id
  - tenant_id
  - location_id (optional)
  - user_id
  - role (owner, admin, manager, staff)
  - is_active (flag)

- **Relations:**
  - belongs to User
  - belongs to Tenant
  - optionally belongs to Location

### 3.5 StaffMember

- **Description:**
    Мастер, оказывающий услуги для бизнеса (tenant'а).

- **Key fields:**
  - id
  - user_id (optional)
  - display_name
  - bio (optional)
  - color_hex (optional)
  - location_id (optional)
  - is_active (flag)
  - created_at, updated_at
  
- **Relations:**
  - belongs to Tenant
  - belongs to Location
  - belongs to User
  - has many WorkSchedules
  - has many Bookings
  - has many TimeSlot
  - has many Services (many-to-many)

### 3.6 Service

- **Description:**
    Услуга, оказываемая в локации владельца бизнеса (tenant'а).

- **Key fields:**
  - id
  - tenant_id
  - name
  - duration_minutes
  - price_minor
  - currency
  - description (optional)
  - image_url (optional)
  - location_id (optional)
  - is_active (flag)
  - created_at, updated_at

- **Relations:**
  - belongs to Tenant
  - optionally belongs to Location (если услуги отличаются в зависимости от локации)
  - has many StaffMembers (many-to-many)
  - has many Bookings

### 3.7 StaffService

- **Description:**
    Ассоциативная таблица для связи m2m между Service и StaffMember.

- **Key fields:**
  - id
  - tenant_id
  - staff_member_id
  - service_id
  - custom_price_minor (optional)
  - custom_duration_minutes (optional)
  - location_id (optional)
  - is_featured (flag)
  - created_at, updated_at

- **Relations:**
  - belongs to StaffMember
  - belongs to Service

### 3.8 Customer

- **Description:**
    Конечный пользователь, который бронирует услуги с помощью Sentio.

- **Key fields:**
  - id
  - telegram_id
  - phone (optional)
  - first_name
  - last_name
  - avatar_url (optional)
  - created_at, updated_at
  
- **Relations:**
  - has many FavoriteLocations (через отдельные таблицы избранного)
  - has many TenantCustomers

### 3.9 TenantCustomer

- **Description:**
    Конечный пользователь для конкретного Tenant, который бронирует услуги с помощью Sentio.

- **Key fields:**
  - id
  - customer_id
  - tenant_id
  - payment_method_id
  - card_last_4 (optional)
  - card_brand
  - last_booking_status
  - late_cancellation (flag)
  - is_active (flag)
  - created_at, updated_at
  
- **Relations:**
- - has many Bookings
  - belongs to Tenant
  - belongs to Customer

### 3.10 WorkSchedule

- **Description:**
    Рабочее расписание сотрудника бизнеса.

- **Key fields:**
  - id
  - tenant_id
  - staff_member_id
  - work_date
  - start_at
  - end_at
  - created_at, updated_at

- **Relations:**
  - belongs to StaffMember
  - used to generate TimeSlots

### 3.11 TimeSlot

- **Description:**
    Конкретный промежуток времени, который может быть использован 
    для бронирования определённого мастера и услуги.

- **Key fields:**
  - id
  - tenant_id
  - staff_member_id
  - work_schedule_id
  - start_time
  - end_time
  - status (available / blocked / booked / expired)
  - created_at, updated_at
  
- **Relations:**
  - belongs to WorkSchedule
  - belongs to StaffMember
  - has zero or one Booking

### 3.12 Booking

- **Description:**
    Резервация временного промежутка (time slot) конечным пользователем.

- **Key fields:**
  - id
  - tenant_id
  - customer_id
  - staff_member_id
  - service_id
  - timeslot_id
  - booking_status (confirmed / cancelled / no_show / done / no_history)
  - created_at, updated_at
  
- **Relations:**
  - belongs to Tenant
  - belongs to TenantCustomer
  - belongs to StaffMember
  - belongs to Service
  - belongs to TimeSlot


## 4. Business rules

- Rule 1: Одна активная бронь (со статусом confirmed) на TimeSlot, 
  одновременно не может быть двух confirmed для одного и того же TimeSlot.
- Rule 2: Отсутствие возможности бронировать слоты в прошлом.
- Rule 3: Учитываем часовой пояс tenant при расчёте прошлого/будущего.
- Rule 4: TimeSlot может быть только в пределах рабочего времени мастера.
- Rule 5: Переходы между статусами брони возможны только из confirmed в cancelled и из confirmed в "no-show", 
  но не наоборот. Статус "no-show" выставляет система.
- Rule 6: Управлять расписанием мастеров и услугами может только администратор или владелец бизнеса.
- Rule 7: Порог поздней отмены (настраивается, например 120 минут).
- Rule 8: "no-show" определяется как:
          - клиент не пришёл на запись, и она не была отменена до начала;
- Rule 9: Система может хранить счётчики no-show и late cancellations per TenantCustomer.


## 5. Main flows (Scenarios)

### 5.1 Create booking

1. Клиент открывает телеграм-бот и выбирает сервис (по прямой ссылке или через поиск).
2. Выбирает нужную услугу и опционально мастера.
3. Sentio загружает график сотрудников и существующие брони, генерирует доступные слоты для бронирования.
4. Клиент выбирает свободный тайм слот.
5. Система валидирует:
 - слот всё ещё свободен,
 - слот в будущем времени,
 - статус сотрудника активен.
6. Система создаёт Booking (status = confirmed) и связывает его с выбранным TimeSlot.
7. Sentio отправляет уведомления клиенту и сотруднику.

### 5.2 Cancel booking

1. Клиент открывает личный кабинет в телеграм-боте.
2. Выбирает Booking, который хочет отменить.
3. Система валидирует:
 - время до начала сеанса,
 - last_booking_status != "no-show",
 - Booking действительно активен,
 - Booking связан с этим клиентом.
4. Если время до начала сеанса меньше либо равно порогу поздней отмены (см. Rule 7), 
   система применяет правила отмены/переноса для данного бронирования 
   (смотри в section 6. Penalty & cancellation policy).
5. Система отменяет Booking (status = cancelled) и освобождает TimeSlot для StaffMember'а.
6. Sentio отправляет уведомления клиенту и сотруднику.

### 5.3 Change booking

1. Клиент открывает личный кабинет в телеграм-боте.
2. Выбирает Booking, который хочет перенести.
3. Система валидирует:
 - время до начала сеанса,
 - last_booking_status != "no-show",
 - Booking действительно активен,
 - Booking связан с этим клиентом.
4. Если время до начала сеанса меньше либо равно порогу поздней отмены (см. Rule 7), 
   система применяет правила отмены/переноса для данного бронирования 
   (смотри в section 6. Penalty & cancellation policy).
5. Система предлагает выбрать услугу и опционально мастера.
6. Клиент выбирает нужную услугу и опционально мастера.
7. Sentio загружает график сотрудников и существующие брони, генерирует доступные слоты для бронирования.
8. Клиент выбирает свободный тайм слот.
9. Система валидирует:
 - слот всё ещё свободен,
 - слот в будущем времени,
 - статус сотрудника активен.
10. Система отменяет исходный Booking (status = cancelled) и создаёт новый Booking, 
    привязанный к новому TimeSlot.
11. Sentio отправляет уведомления клиенту и сотруднику.

### 5.4 Configure staff schedule
(будет заполнен, перед тем как буду писать модуль расписания)

### 5.5 Configure service
(будет заполнен, перед тем как буду писать модуль изменения услуги)


## 6. Penalty & cancellation policy (advanced)

- Rule 1: Правила отмены/переноса бронирования для клиента:
  - Клиент имеет право отменить/перенести бронирование неограниченное количество раз, если сделает это
  не позднее чем за 24 часа до начала сеанса.
  - Клиент может бесплатно отменить/перенести бронирование позднее чем за 120 минут до начала сеанса
  только один раз.
  - Если клиент отменил/перенёс бронирование за <= 119 минут до начала сеанса, 
  статус его бронирования считается "no-show".
  - Если статус последнего бронирования клиента "no-show", при следующей отмене/переносе за <= 119 минут 
  до начала сеанса, клиент получает сообщение с предупреждением о списании штрафной санкции 
  в размере 40% от стоимости услуги с привязанной карты и угрозе бана аккаунта при повторном инциденте.
  - Если статус последнего бронирования клиента "no-show" и late_cancellation = True, при повторной 
  отмене/переносе за <= 119 минут до начала сеанса, клиент получает сообщение с предупреждением 
  о списании штрафной санкции в размере 40% от стоимости услуги с привязанной карты и бане аккаунта.
  - Если банковская карта не привязана, то клиент получает сообщение о просьбе привязать банковскую карту. 
  - Если клиент отказывается привязать банковскую карту, то он получает сообщение 
  о добавлении аккаунта в чёрный список.

- Rule 2: Если клиент вовремя не перенёс/отменил и не явился на сеанс, к нему применяется Rule 1.
