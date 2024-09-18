from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import constants
import models
from bot_routers.general_buttons import home_markup
from config import SERVER_URL
from database import sessionLocal
from panel_api import create_config_string, get_client_info, delete_client, get_client, add_client, update_client
from raw_texts import BACK
from utils.actions import add_task, is_task_expired, expired_message, tap_to_coppy, escape, server_not_available
from datetime import datetime
from utils.actions import callback_data_encoder
from utils.expire_time import expiration_time


async def services_manage_steps(data: dict, update: Update, context: CallbackContext):
    step = data["step"]
    services_id = data["id"]

    discount = None

    try:
        if data["d_c"]:
            discount = data["d_c"]
    except Exception as ex:
        print(ex)

    # ----------------------------- Expire Message -----------------------------------

    if await is_task_expired(update, context) and services_id != 0 and not discount:
        await expired_message(update, context)
        return

    # ----------------------------- Service Management Steps -------------------------

    if step == 0:
        services_id = data["id"]

        db = sessionLocal()
        services = db.query(models.UsersServices).join(
            models.Users
        ).where(
            models.Users.Chat_Id == update.effective_chat.id
        ).all()

        if services.__contains__(None):
            await server_not_available(update, context)
            return

        buttons_keys = []

        temp_button = []

        for i in services:
            callback_data = data.copy()
            callback_data["id"] = i.Id
            callback_data["step"] = 1

            encode = callback_data_encoder(callback_data)

            temp_button.append(
                InlineKeyboardButton(
                    i.Email,
                    callback_data=encode
                ),
            )
            if len(temp_button) == 2 or i.Id == services[-1].Id:
                buttons_keys.append(temp_button)
                temp_button = []

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

        if len(services) != 0:
            choose_service = "سرویس مورد نظر را انتخاب کنید"
            if services_id == 0:
                message = await context.bot.send_message(
                    reply_to_message_id=update.effective_message.message_id,
                    chat_id=update.effective_chat.id,
                    text=choose_service,
                    reply_markup=buttons_markup,
                )
                await add_task(update.effective_user.id, message.message_id)

            if services_id == -1:
                await update.effective_message.edit_text(
                    text=choose_service,
                    reply_markup=buttons_markup,
                )
        else:
            a = "شما هنوز سرویسی ندارید!"
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'{a}',
            )

    if step == 1:
        db = sessionLocal()

        user_service = db.query(models.UsersServices).where(
            models.UsersServices.Id == services_id
        ).first()

        inbound = db.query(models.Inbounds).where(
            models.Inbounds.Id == user_service.Inbound_Id
        ).first()

        if user_service.Test_Inbound_Id:
            inbound = db.query(models.TestInbounds).where(
                models.TestInbounds.Id == user_service.Test_Inbound_Id
            ).first()

        if not user_service or not inbound:
            await server_not_available(update, context)
            return

        services = "💎 سرویس انتخابی شما: "
        test_services = "🧪 سرویس تست" + "\n\n" if not user_service.Subscription_Id else ""
        location = f" 🌐 سرور:  {inbound.Remark}"
        email = f" 🌿 نام: {user_service.Email}"
        nou = f" 👤 تعداد کاربر:  {user_service.Number_Of_Users}"
        m = f" 📆 مدت زمان:  {int(user_service.Days / 30)} ماهه" if user_service.Days >= 30 else f" 📆 مدت زمان:  {int(user_service.Days)} روزه"
        gb = f" 📦 حجم سرویس:  {constants.data_size(user_service.Total_GB) if user_service.Total_GB > 0 else 'نامحدود'}"

        next_2 = data.copy()
        next_2["step"] = 2

        next_3 = data.copy()
        next_3["step"] = 3

        next_4 = data.copy()
        next_4["step"] = 4

        next_9 = data.copy()
        next_9["step"] = 9

        next_11 = data.copy()
        next_11["step"] = 11

        back_state = data.copy()
        back_state["id"] = -1
        back_state["step"] = 0

        if user_service.Subscription_Id:

            buttons_key = [
                [
                    InlineKeyboardButton(
                        "ℹ️" + " اطلاعات سرویس",
                        callback_data=callback_data_encoder(next_2),
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "⚡️ بروزرسانی سرویس",
                        callback_data=callback_data_encoder(next_3),
                    ),
                    InlineKeyboardButton(
                        "♻️  تمدید سرویس",
                        callback_data=callback_data_encoder(next_4),
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "🗑  حذف سرویس",
                        callback_data=callback_data_encoder(next_9),
                    ),

                    InlineKeyboardButton(
                        "🌐  لینک سرویس",
                        callback_data=callback_data_encoder(next_11),
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "❌  بستن پنل",
                        callback_data="close"
                    ),
                    InlineKeyboardButton(
                        BACK,
                        callback_data=callback_data_encoder(back_state),
                    ),

                ],
            ]
        else:
            buttons_key = [
                [
                    InlineKeyboardButton(
                        "⚡️ بروزرسانی سرویس",
                        callback_data=callback_data_encoder(next_3),
                    ),
                    InlineKeyboardButton(
                        "ℹ️" + " اطلاعات سرویس",
                        callback_data=callback_data_encoder(next_2),
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "🗑  حذف سرویس",
                        callback_data=callback_data_encoder(next_9),
                    ),

                    InlineKeyboardButton(
                        "🌐  لینک سرویس",
                        callback_data=callback_data_encoder(next_11),
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "❌  بستن پنل",
                        callback_data="close"
                    ),
                    InlineKeyboardButton(
                        BACK,
                        callback_data=callback_data_encoder(back_state),
                    ),
                ],
            ]

        buttons_markup = InlineKeyboardMarkup(buttons_key)

        await update.effective_message.edit_text(
            text=f"{services}\n\n{test_services}{location}\n\n{email}\n\n{nou}\n\n{m}\n\n{gb}",
            reply_markup=buttons_markup,
        )
        db.close()

    if step == 2:

        db = sessionLocal()

        user_service = db.query(models.UsersServices).where(
            models.UsersServices.Id == services_id
        ).first()

        inbound = db.query(models.Inbounds).where(
            models.Inbounds.Id == user_service.Inbound_Id
        ).first()

        if user_service.Test_Inbound_Id:
            inbound = db.query(models.TestInbounds).where(
                models.TestInbounds.Id == user_service.Test_Inbound_Id
            ).first()

        server = db.query(models.Servers).where(
            models.Servers.Id == inbound.Server_Id,
        ).first()

        stats = get_client_info(
            panel_url=server.Url,
            username=server.UserName,
            password=server.Password,
            inbound_id=inbound.Panel_Inbound_Id,
            email=user_service.Email,
        )

        if not user_service or not inbound or not server or not stats:
            await server_not_available(update, context)
            return

        services = "💎 سرویس انتخابی شما: "
        test_services = "🧪 سرویس تست" + "\n\n" if not user_service.Subscription_Id else ""
        email = f" 🌿 نام:  {user_service.Email}"
        usage = f" ⬇️ حجم مصرف شده:  {constants.data_size(user_service.Usage)}"
        remained = f" 📊 حجم باقی مانده:  {constants.data_size(user_service.Remained)}" + "\n\n" if user_service.Total_GB > 0 else ""
        total = f" ♾️ آستانه مصرف:  {constants.data_size(user_service.Total_GB) if user_service.Total_GB > 0 else 'نامحدود'}"
        expiry_time = f" 📆 تاریخ انقضا:  {stats['expiry_time']}"

        back_state = data.copy()
        back_state["step"] = 1

        back_state_key = [
            [
                InlineKeyboardButton(
                    BACK,
                    callback_data=callback_data_encoder(back_state),
                )
            ],
        ]

        back_state_markup = InlineKeyboardMarkup(back_state_key)

        await update.effective_message.edit_text(
            text=f"{services}\n\n{test_services}{email}\n\n{usage}\n\n{remained}{total}\n\n{expiry_time}",
            reply_markup=back_state_markup,
        )

        db.close()

    if step == 3:
        db = sessionLocal()

        user_service = db.query(
            models.UsersServices,
        ).where(
            models.UsersServices.Id == services_id
        ).first()

        inbound = db.query(models.Inbounds).where(
            models.Inbounds.Id == user_service.Inbound_Id,
        ).first()

        if user_service.Test_Inbound_Id:
            inbound = db.query(models.TestInbounds).where(
                models.TestInbounds.Id == user_service.Test_Inbound_Id,
            ).first()

        server = db.query(models.Servers).where(
            models.Servers.Id == inbound.Server_Id
        ).first()

        back_state = data.copy()
        back_state["step"] = 1

        buttons_key = [
            [
                InlineKeyboardButton(
                    BACK,
                    callback_data=callback_data_encoder(back_state),
                )
            ],
        ]

        buttons_markup = InlineKeyboardMarkup(buttons_key)

        if get_client(
                panel_url=server.Url,
                username=server.UserName,
                password=server.Password,
                inbound_id=inbound.Panel_Inbound_Id,
                email=user_service.Email,
        ):
            await update.callback_query.answer(
                text=f" سرویس {user_service.Email} نیازی به بروزرسانی ندارد. ",
                show_alert=True,
            )
        else:
            config_url, email, client_id = add_client(
                panel_url=server.Url,
                username=server.UserName,
                password=server.Password,
                address=inbound.Address,
                sni=inbound.Sni,
                inbound_id=inbound.Panel_Inbound_Id,
                ip_limit=user_service.Number_Of_Users,
                expire_time=int(user_service.ExpirationDate.timestamp() * 1000),
                total_gb=user_service.Remained,
                client_id=user_service.UUID,
                email=user_service.Email,
            )

            connection_link = "لینک سرویس:"
            text = escape(f"{connection_link}\n\n{tap_to_coppy(config_url)}")
            await update.effective_message.edit_text(
                text=text,
                reply_markup=buttons_markup,
                parse_mode="MarkdownV2",
            )

    if step == 4:

        db = sessionLocal()

        subscriptions = db.query(models.Subscriptions).distinct().all()

        if not subscriptions:
            await server_not_available(update, context)
            return

        number_of_users = []
        controls_keys = []

        for i in subscriptions:
            if i.Number_Of_Users not in number_of_users:
                callback_data = data.copy()
                callback_data["u"] = i.Id
                callback_data["step"] = 5
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

        controls_markup = InlineKeyboardMarkup(
            controls_keys
        )

        db.close()

        nou = "تعداد کاربران را انتخاب کنید"
        await update.effective_message.edit_text(
            text=nou,
            reply_markup=controls_markup,
        )

    if step == 5:
        db = sessionLocal()

        print(data)

        single_subscription = db.query(models.Subscriptions).where(
            models.Subscriptions.Id == data["u"]
        ).first()

        subscriptions = db.query(models.Subscriptions).distinct().where(
            models.Subscriptions.Number_Of_Users == single_subscription.Number_Of_Users
        ).all()

        if not single_subscription or not subscriptions:
            await server_not_available(update, context)
            return

        month = []
        controls_keys = []

        for i in subscriptions:
            if i.Days not in month:
                callback_data = data.copy()
                callback_data["m"] = i.Id
                callback_data["step"] = 6
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
        back_state["step"] = 4

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

    if step == 6:
        db = sessionLocal()

        print(data)

        single_subscription = db.query(models.Subscriptions).where(
            models.Subscriptions.Id == data["m"]
        ).first()

        subscriptions = db.query(models.Subscriptions).distinct().where(
            models.Subscriptions.Number_Of_Users == single_subscription.Number_Of_Users,
            models.Subscriptions.Days == single_subscription.Days,
        ).all()

        if not single_subscription or not subscriptions:
            await server_not_available(update, context)
            return

        total_gb = []
        controls_keys = []

        for i in subscriptions:
            if i.Total_GB not in total_gb:
                callback_data = data.copy()
                callback_data["gb"] = i.Id
                callback_data["step"] = 7

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
        back_state["step"] = 5

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

    if step == 7:
        db = sessionLocal()

        single_subscription = db.query(models.Subscriptions).where(
            models.Subscriptions.Id == data["gb"]
        ).first()

        user_service, user, subscription, inbound = db.query(
            models.UsersServices,
            models.Users,
            models.Subscriptions,
            models.Inbounds
        ).join(
            models.Users
        ).join(
            models.Subscriptions
        ).join(
            models.Inbounds
        ).where(
            models.UsersServices.Id == services_id
        ).first()

        if not single_subscription or not user_service or not user or not subscription or not inbound:
            await server_not_available(update, context)
            return

        to_extend = data.copy()
        to_extend["step"] = 8

        context.user_data["data"] = data.copy()

        back_state = data.copy()
        back_state["step"] = 6

        title = "♻️ تمدید سرویس" + "\n" if discount else ""
        services = "💎 سرویس انتخابی شما:"
        email = f"🌿 نام:  {user_service.Email}"
        location = f"🌐 لوکیشن:  {inbound.Remark}"
        nou = f"👤 تعداد کاربر:  {single_subscription.Number_Of_Users}"
        m = f"📆 مدت زمان:  {int(single_subscription.Days / 30)} ماهه"
        total_gb = f"📦 حجم سرویس:  {single_subscription.Total_GB} گیگ" if single_subscription.Total_GB != 0 else f"📦 حجم سرویس:  نامحدود"

        controls_key = [
            [
                InlineKeyboardButton(
                    f"{single_subscription.Price} تومان",
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
                    callback_data=callback_data_encoder(to_extend),
                ),
            ],
        ]

        if discount:
            deducted = int((single_subscription.Price * discount) / 100)
            price_with_discount = single_subscription.Price - deducted
            controls_key = [
                [
                    InlineKeyboardButton(
                        f"{single_subscription.Price} تومان",
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
                        callback_data=callback_data_encoder(to_extend),
                    ),
                ],
            ]

        buttons_markup = InlineKeyboardMarkup(controls_key)

        if discount:
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="\u202B" + f"{title}{services}\n{email}\n{location}\n{nou}\n{m}\n{total_gb}",
                reply_markup=buttons_markup,
            )
            await add_task(update.effective_user.id, message.message_id)
        else:
            await update.effective_message.edit_text(
                text="\u202B" + f"{title}{services}\n{email}\n{location}\n{nou}\n{m}\n{total_gb}",
                reply_markup=buttons_markup,
            )
        db.close()

    if step == 8:
        if discount:
            if await is_task_expired(update, context) and services_id != 0:
                await expired_message(update, context)
                return

        db = sessionLocal()

        single_subscription = db.query(models.Subscriptions).where(
            models.Subscriptions.Id == data["gb"]
        ).first()

        user_service, user, subscription, inbound = db.query(
            models.UsersServices,
            models.Users,
            models.Subscriptions,
            models.Inbounds
        ).join(
            models.Users
        ).join(
            models.Subscriptions
        ).join(
            models.Inbounds
        ).where(
            models.UsersServices.Id == services_id
        ).first()

        server = db.query(models.Servers).where(
            models.Servers.Id == inbound.Server_Id
        ).first()

        stats = get_client_info(
            panel_url=server.Url,
            username=server.UserName,
            password=server.Password,
            inbound_id=inbound.Panel_Inbound_Id,
            email=user_service.Email,
        )

        if not single_subscription or not user_service or not user or not subscription or not inbound or not stats:
            await server_not_available(update, context)
            return

        if stats["expiry_time"] == 0 or stats["total"] == 0:
            await update.callback_query.answer(
                text=f" سرویس {user_service.Email} نیازی به تمدید ندارد. ",
                show_alert=True,
            )
        else:
            now = datetime.now()
            date = datetime.strptime(stats["expiry_time"], "%d-%m-%Y")
            expiry_time = date < now

            if expiry_time or stats["expired_volume"]:

                if user.Wallet >= subscription.Price:

                    subscription = db.query(models.Subscriptions).distinct().where(
                        models.Subscriptions.Number_Of_Users == single_subscription.Number_Of_Users,
                        models.Subscriptions.Days == single_subscription.Days,
                        models.Subscriptions.Total_GB == single_subscription.Total_GB,
                    ).first()

                    expire_time, raw_time = expiration_time(days=subscription.Days)

                    client = update_client(
                        panel_url=server.Url,
                        username=server.UserName,
                        password=server.Password,
                        inbound_id=inbound.Panel_Inbound_Id,
                        ip_limit=single_subscription.Number_Of_Users,
                        expire_time=expire_time,
                        total_gb=single_subscription.Total_GB * constants.gb_size,
                        client_id=user_service.UUID,
                        email=user_service.Email,
                    )

                    if client:
                        user.Wallet -= subscription.Price
                        user_service.Total_GB = subscription.Total_GB * constants.gb_size
                        user_service.Remained = 0

                        await update.effective_message.edit_text(
                            text=f"سرویس{user_service.Email} با موفقیت تمدید شد ",
                        )
                    else:
                        await update.callback_query.answer(
                            text="خطایی رخ داد!",
                            show_alert=True,
                        )
                else:
                    await update.callback_query.answer(
                        text="موجودی شما برای تمدید این سرویس کافی نیست\nشما میتوانید اعتبار کیف پول خود را از بخش "
                             "کیف پول افزایش دهید",
                        show_alert=True,
                    )
            else:
                await update.callback_query.answer(
                    text=f"سرویس{user_service.Email} هنوز اعتبار دارد",
                    show_alert=True,
                )

        db.commit()
        db.close()

    if step == 9:
        confirm_delete = data.copy()
        confirm_delete["step"] = 10

        back_state = data.copy()
        back_state["step"] = 1

        buttons_key = [
            [
                InlineKeyboardButton(
                    "بله",
                    callback_data=callback_data_encoder(confirm_delete),
                ),
                InlineKeyboardButton(
                    "خیر",
                    callback_data=callback_data_encoder(back_state),
                )
            ],
            [
                InlineKeyboardButton(
                    "❌  بستن پنل",
                    callback_data="close"
                )
            ]
        ]

        buttons_markup = InlineKeyboardMarkup(buttons_key)

        await update.effective_message.edit_text(
            text="از حذف این سرویس مظمئن هستید؟",
            reply_markup=buttons_markup,
        )

    if step == 10:
        db = sessionLocal()

        user_service = db.query(models.UsersServices).where(
            models.UsersServices.Id == services_id
        ).first()

        inbound = db.query(models.Inbounds).where(
            models.Inbounds.Id == user_service.Inbound_Id
        ).first()

        if user_service.Test_Inbound_Id:
            inbound = db.query(models.TestInbounds).where(
                models.TestInbounds.Id == user_service.Test_Inbound_Id
            ).first()

        server = db.query(models.Servers).where(
            models.Servers.Id == inbound.Server_Id,
        ).first()

        if not user_service or not inbound or not server:
            await server_not_available(update, context)
            return

        delete = delete_client(
            panel_url=server.Url,
            username=server.UserName,
            password=server.Password,
            inbound_id=inbound.Panel_Inbound_Id,
            client_id=user_service.UUID,
        )
        if delete:
            db.delete(user_service)
            db.commit()
            db.close()
            await update.callback_query.delete_message()

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"سرویس {user_service.Email} با موفقیت حذف شد",
                reply_markup=home_markup,
            )
        else:
            await update.callback_query.delete_message()

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="خطایی رخ داد.",
                reply_markup=home_markup,
            )

    if step == 11:
        db = sessionLocal()

        user_service = db.query(models.UsersServices).where(
            models.UsersServices.Id == services_id
        ).first()

        inbound = db.query(models.Inbounds).where(
            models.Inbounds.Id == user_service.Inbound_Id
        ).first()

        if user_service.Test_Inbound_Id:
            inbound = db.query(models.TestInbounds).where(
                models.TestInbounds.Id == user_service.Test_Inbound_Id
            ).first()

        if not user_service or not inbound:
            await server_not_available(update, context)
            return

        network = constants.Network.tcp.value
        security = constants.Security.tls.value
        header_type = constants.HeaderType.none.value

        if inbound.Network == constants.Network.tcp:
            network = constants.Network.tcp.value

        if inbound.Network == constants.Network.ws:
            network = constants.Network.ws.value

        if inbound.Security == constants.Security.none:
            security = constants.Security.none.value

        if inbound.Security == constants.Security.tls:
            security = constants.Security.tls.value

        if inbound.HeaderType == constants.HeaderType.none:
            header_type = constants.HeaderType.none.value

        if inbound.HeaderType == constants.HeaderType.http:
            header_type = constants.HeaderType.http.value

        config_url = create_config_string(
            email=user_service.Email,
            address=inbound.Address,
            sni=inbound.Sni,
            client_id=user_service.UUID,
            port=inbound.Inbound_Port,
            network=network,
            security=security,
            header_type=header_type,
        )

        back_state = data.copy()
        back_state["step"] = 1

        back_state_key = [
            [
                InlineKeyboardButton(
                    BACK,
                    callback_data=callback_data_encoder(back_state),
                )
            ],
        ]

        back_state_markup = InlineKeyboardMarkup(back_state_key)

        if config_url:
            connection_link = "لینک اتصال:"
            # info_link = "لینک اطلاعات سرویس:"
            # information = f"{SERVER_URL}/api/v2/config/information?service_id={services_id}"
            # text = escape(f"{connection_link}\n\n{tap_to_coppy(config_url)}\n\n{info_link}\n\n{information}")
            text = escape(f"{connection_link}\n\n{tap_to_coppy(config_url)}")
            await update.effective_message.edit_text(
                text=text,
                reply_markup=back_state_markup,
                parse_mode="MarkdownV2"
            )
        else:
            b = "سرور در دسترس نیست!!"
            await update.effective_message.edit_text(
                text=f'{b}',
                reply_markup=back_state_markup,
            )
        db.close()
