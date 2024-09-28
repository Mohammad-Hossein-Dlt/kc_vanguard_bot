from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import models
from constants import gb_size
from database import sessionLocal
from panel_api import add_client, inbound_client_len
from raw_texts import BACK
from utils.actions import add_task, is_task_expired, expired_message, tap_to_coppy, escape, server_not_available
from utils.actions import callback_data_encoder
from utils.expire_time import expiration_time


async def buy_steps(data: dict, update: Update, context: CallbackContext):
    step = data["step"]
    inbound_id = data["i_id"]

    discount = None

    try:
        if data["d_c"]:
            discount = data["d_c"]
    except Exception as ex:
        print(ex)

    # ----------------------------- Expire Message -------------------------

    if await is_task_expired(update, context) and inbound_id != 0 and not discount:
        await expired_message(update, context)
        return

    # ----------------------------- Buy Service --------------------------

    if step == 0:

        db = sessionLocal()

        inbounds_with_servers = db.query(models.Inbounds, models.Servers).join(
            models.Servers
        ).all()

        if not inbounds_with_servers:
            await server_not_available(update, context)
            return

        buttons_keys = [
            [
                InlineKeyboardButton(
                    "ظرفیت",
                    callback_data="None1"
                ),
                InlineKeyboardButton(
                    "نام سرور",
                    callback_data="None2"
                ),
            ]
        ]

        for inbound, server in inbounds_with_servers:
            length = inbound_client_len(server.Url, server.UserName, server.Password, inbound.Panel_Inbound_Id)
            remained = inbound.Limit - length if length else 0
            capacity = f"{remained} نفر " if remained > 0 else "ندارد"

            callback_data = data.copy()
            callback_data["i_id"] = inbound.Id
            callback_data["step"] = 1

            encode = callback_data_encoder(callback_data)

            buttons_keys.append(
                [
                    InlineKeyboardButton(
                        capacity,
                        callback_data=f"None{inbound.Id}X"
                    ),
                    InlineKeyboardButton(
                        inbound.Remark,
                        callback_data=encode
                    ),
                ]
            )

        buttons_keys.append(
            [
                InlineKeyboardButton(
                    "❌  بستن پنل",
                    callback_data="close"
                )
            ]
        )

        buttons_markup = InlineKeyboardMarkup(buttons_keys)

        db.close()
        choose_location = "سرور مورد نظر را انتخاب کنید"

        if inbound_id == 0:
            message = await context.bot.send_message(
                reply_to_message_id=update.effective_message.message_id,
                chat_id=update.effective_chat.id,
                text=choose_location,
                reply_markup=buttons_markup,
            )
            await add_task(update.effective_user.id, message.message_id)

        if inbound_id == -1:
            await update.effective_message.edit_text(
                text=choose_location,
                reply_markup=buttons_markup,
            )

    if step == 1:

        db = sessionLocal()

        inbound, server = db.query(models.Inbounds, models.Servers).join(
            models.Servers
        ).where(
            models.Inbounds.Id == inbound_id
        ).first()

        subscription = db.query(models.Subscriptions).distinct().all()

        length = inbound_client_len(server.Url, server.UserName, server.Password, inbound.Panel_Inbound_Id)

        if not inbound or not server or not subscription or not length:
            await server_not_available(update, context)
            return

        remained = inbound.Limit - length

        if remained < 1:
            await update.callback_query.answer(
                text="ظرفیت این سرور تکمیل شده است!",
                show_alert=True,
            )
            return

        number_of_users = []
        controls_keys = []

        for i in subscription:
            if i.Number_Of_Users not in number_of_users:
                callback_data = data.copy()
                callback_data["u"] = i.Id
                callback_data["step"] = 2
                encode = callback_data_encoder(callback_data)

                controls_keys.append(
                    [
                        InlineKeyboardButton(
                            f"{i.Number_Of_Users} کاربره",
                            callback_data=encode
                        ),
                    ]
                )
                number_of_users.append(i.Number_Of_Users)

        back_state = data.copy()
        back_state["i_id"] = -1
        back_state["step"] = 0

        controls_keys.append(
            [
                InlineKeyboardButton(
                    "❌  بستن پنل",
                    callback_data="close"
                ),
                InlineKeyboardButton(
                    BACK,
                    callback_data=callback_data_encoder(back_state),
                ),
            ]
        )

        controls_markup = InlineKeyboardMarkup(
            controls_keys
        )

        db.close()

        nou = "تعداد کاربران را انتخاب کنید"
        await update.effective_message.edit_text(
            text=nou,
            reply_markup=controls_markup,
        )

    if step == 2:
        db = sessionLocal()

        print(data)

        single_subscription = db.query(models.Subscriptions).where(
            models.Subscriptions.Id == data["u"]
        ).first()

        subscription = db.query(models.Subscriptions).distinct().where(
            models.Subscriptions.Number_Of_Users == single_subscription.Number_Of_Users
        ).all()

        if not single_subscription or not subscription:
            await server_not_available(update, context)
            return

        month = []
        controls_keys = []

        for i in subscription:
            if i.Days not in month:
                callback_data = data.copy()
                callback_data["m"] = i.Id
                callback_data["step"] = 3
                encode = callback_data_encoder(callback_data)

                controls_keys.append(
                    [
                        InlineKeyboardButton(
                            text=f"{int(i.Days / 30)} ماهه",
                            callback_data=encode
                        ),
                    ]
                )
                month.append(i.Days)

        back_state = data.copy()
        back_state["step"] = 1

        controls_keys.append(
            [
                InlineKeyboardButton(
                    "❌  بستن پنل",
                    callback_data="close"
                ),
                InlineKeyboardButton(
                    BACK,
                    callback_data=callback_data_encoder(back_state),
                ),
            ]
        )

        controls_markup = InlineKeyboardMarkup(controls_keys)
        db.close()

        m = "تعداد ماه را انتخاب کنید"
        await update.effective_message.edit_text(
            text=m,
            reply_markup=controls_markup,
        )
    if step == 3:
        db = sessionLocal()

        print(data)

        single_subscription = db.query(models.Subscriptions).where(
            models.Subscriptions.Id == data["m"]
        ).first()

        subscription = db.query(models.Subscriptions).distinct().where(
            models.Subscriptions.Number_Of_Users == single_subscription.Number_Of_Users,
            models.Subscriptions.Days == single_subscription.Days,
        ).all()

        if not single_subscription or not subscription:
            await server_not_available(update, context)
            return

        total_gb = []
        controls_keys = []

        for i in subscription:
            if i.Total_GB not in total_gb:
                callback_data = data.copy()
                callback_data["gb"] = i.Id
                callback_data["step"] = 4

                encode = callback_data_encoder(callback_data)

                controls_keys.append(
                    [
                        InlineKeyboardButton(
                            text=f"{i.Total_GB} گیگ" if i.Total_GB != 0 else "نامحدود",
                            callback_data=encode
                        ),
                    ]
                )
                total_gb.append(i.Total_GB)

        back_state = data.copy()
        back_state["step"] = 2

        controls_keys.append(
            [
                InlineKeyboardButton(
                    "❌  بستن پنل",
                    callback_data="close"
                ),
                InlineKeyboardButton(
                    BACK,
                    callback_data=callback_data_encoder(back_state),
                ),
            ]
        )

        controls_markup = InlineKeyboardMarkup(controls_keys)
        db.close()

        gb = "مقدار حجم را انتخاب کنید"

        await update.effective_message.edit_text(
            text=gb,
            reply_markup=controls_markup,
        )

    if step == 4:
        db = sessionLocal()

        print(len(data))

        single_subscription = db.query(models.Subscriptions).where(
            models.Subscriptions.Id == data["gb"]
        ).first()

        subscription = db.query(models.Subscriptions).distinct().where(
            models.Subscriptions.Number_Of_Users == single_subscription.Number_Of_Users,
            models.Subscriptions.Days == single_subscription.Days,
            models.Subscriptions.Total_GB == single_subscription.Total_GB,
        ).first()

        user = db.query(models.Users).where(
            models.Users.Chat_Id == update.effective_chat.id,
        ).first()

        inbound = db.query(models.Inbounds).distinct().where(
            models.Inbounds.Id == inbound_id,
        ).first()

        if not single_subscription or not subscription or not user or not inbound:
            await server_not_available(update, context)
            return

        callback_data = data.copy()
        callback_data["step"] = 5

        encode = callback_data_encoder(callback_data)

        context.user_data["data"] = data.copy()

        back_state = data.copy()
        back_state["step"] = 3

        title = "🛒 خرید سرویس" + "\n" if discount else ""
        services = "💎 سرویس انتخابی شما:"
        location = f"🌐 لوکیشن:  {inbound.Remark}"
        nou = f"👤 تعداد کاربر:  {subscription.Number_Of_Users}"
        m = f"📆 مدت زمان:  {int(subscription.Days / 30)} ماهه"
        total_gb = f"📦 حجم سرویس:  {single_subscription.Total_GB} گیگ" if single_subscription.Total_GB != 0 else f"📦 حجم سرویس:  نامحدود"

        controls_key = [
            [
                InlineKeyboardButton(
                    f"{subscription.Price} تومان",
                    callback_data="None1",
                ),
                InlineKeyboardButton(
                    "💰 قیمت سرویس:",
                    callback_data="None2",
                ),
            ],

            [
                InlineKeyboardButton(
                    f"{user.Wallet} تومان",
                    callback_data="None3",
                ),
                InlineKeyboardButton(
                    "💳 اعتبار کیف پول شما:",
                    callback_data="None4",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🎁 اعمال کد تخفیف",
                    callback_data="discount-code",
                ),
            ],
            [
                InlineKeyboardButton(
                    BACK,
                    callback_data=callback_data_encoder(back_state),
                ),
                InlineKeyboardButton(
                    "🛒  خرید",
                    callback_data=encode,
                ),
            ],
        ]

        if discount:
            deducted = int((subscription.Price * discount) / 100)
            price_with_discount = subscription.Price - deducted
            controls_key = [
                [
                    InlineKeyboardButton(
                        f"{subscription.Price} تومان",
                        callback_data="None1",
                    ),
                    InlineKeyboardButton(
                        "💰 قیمت سرویس:",
                        callback_data="None2",
                    ),
                ],

                [
                    InlineKeyboardButton(
                        f"{deducted} تومان",
                        callback_data="None3",
                    ),
                    InlineKeyboardButton(
                        "🎁 تخفیف:",
                        callback_data="None4",
                    ),
                ],

                [
                    InlineKeyboardButton(
                        f"{price_with_discount} تومان",
                        callback_data="None5",
                    ),
                    InlineKeyboardButton(
                        "💝 قیمت با تخفیف:",
                        callback_data="None6",
                    ),
                ],

                [
                    InlineKeyboardButton(
                        f"{user.Wallet} تومان",
                        callback_data="None7",
                    ),
                    InlineKeyboardButton(
                        "💳 اعتبار کیف پول شما:",
                        callback_data="None8",
                    ),
                ],

                [
                    InlineKeyboardButton(
                        "❌  بستن پنل",
                        callback_data="close"
                    ),
                    InlineKeyboardButton(
                        "🛒  خرید",
                        callback_data=encode,
                    ),
                ],
            ]

        controls_markup = InlineKeyboardMarkup(controls_key)
        if discount:
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="\u202B" + f"{title}{services}\n{location}\n{nou}\n{m}\n{total_gb}",
                reply_markup=controls_markup,
            )
            await add_task(update.effective_user.id, message.message_id)
        else:
            await update.effective_message.edit_text(
                text="\u202B" + f"{title}{services}\n{location}\n{nou}\n{m}\n{total_gb}",
                reply_markup=controls_markup,
            )
        db.close()

    if step == 5:
        if discount:
            if await is_task_expired(update, context) and inbound_id != 0:
                await expired_message(update, context)
                return

        db = sessionLocal()

        server, inbound = db.query(models.Servers, models.Inbounds).join(
            models.Inbounds
        ).filter(
            models.Inbounds.Id == inbound_id,
        ).first()

        single_subscription = db.query(models.Subscriptions).where(
            models.Subscriptions.Id == data["gb"]
        ).first()

        subscription = db.query(models.Subscriptions).distinct().where(
            models.Subscriptions.Number_Of_Users == single_subscription.Number_Of_Users,
            models.Subscriptions.Days == single_subscription.Days,
            models.Subscriptions.Total_GB == single_subscription.Total_GB,
        ).first()

        user = db.query(models.Users).where(
            models.Users.Chat_Id == update.effective_chat.id,
        ).first()

        if not server or not inbound or not user or not subscription:
            await server_not_available(update, context)
            return

        if user.Wallet < subscription.Price:
            await update.callback_query.answer(
                text="موجودی شما برای خرید این سرویس کافی نیست\nشما میتوانید اعتبار کیف پول خود را از بخش کیف پول "
                     "افزایش دهید",
                show_alert=True
            )
            return

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="درحال ساخت کانفیگ...",
        )

        expire_time, raw_time = expiration_time(days=subscription.Days)

        config_url, email, client_id = add_client(
            panel_url=server.Url,
            username=server.UserName,
            password=server.Password,
            address=inbound.Address,
            sni=inbound.Sni,
            inbound_id=inbound.Panel_Inbound_Id,
            ip_limit=subscription.Number_Of_Users,
            expire_time=expire_time,
            total_gb=subscription.Total_GB * gb_size,
        )

        if not config_url and not email and not client_id:
            await server_not_available(update, context)
            return

        if config_url and email and client_id:
            deducted = 0
            if discount:
                deducted = (subscription.Price * discount) / 100
            user.Wallet -= (subscription.Price - deducted)

            user_service = models.UsersServices()
            user_service.Inbound_Id = inbound_id
            user_service.Subscription_Id = subscription.Id
            user_service.User_Id = user.Id
            user_service.Email = email
            user_service.UUID = client_id
            user_service.Days = subscription.Days
            user_service.Number_Of_Users = subscription.Number_Of_Users
            user_service.ExpirationDate = raw_time
            user_service.Total_GB = subscription.Total_GB * gb_size

            db.add(user_service)
            db.commit()

            await update.effective_message.delete()

            connection_link = "لینک سرویس:"
            # info_link = "لینک اطلاعات سرویس:"
            # information = f"{SERVER_URL}/api/v2/config/config_information?service_id={user_service.Id}"
            # text = escape(f"{connection_link}\n\n{tap_to_coppy(config_url)}\n\n{info_link}\n\n{information}")
            text = escape(f"{connection_link}\n\n{tap_to_coppy(config_url)}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
                parse_mode="MarkdownV2"
            )

        db.commit()
        db.close()
