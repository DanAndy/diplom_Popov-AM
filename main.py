from typing_extensions import Text
import telebot
import webbrowser
from telebot import types
import sqlite3
import datetime
from datetime import datetime as dtt
from datetime import date
import re
import threading
import time


bot = telebot.TeleBot('6815402908:AAHNJ7Oq4HL3Mdc8hX3BznZmYvxnM1DPI3I')
name = None
date_t = None
step = 0
admins = None
master_r = None
delete_ys = None

watch = 0
watch_m = None

add_zapis = 0
add_zapis_master = None
add_zapis_yslyga = None
add_zapis_data = None
add_zapis_time = None
add_zapis_cikle = None

add_new_master = None
delete_master_m = None
delete_mas_name = None

del_your_zap = 0
mas_znach_na_ydalenie = None

add_yslyga_obsh = 0
check_on_zapis = 0
name_yslyga = None
mas_commands = ["Услуги", "Мои записи", "Добавить администратора", "Удалить свою запись", "Просмотр записей мастера", "Добавление свободной записи","Добавление/Удаление услуги", "Добавление/Удаление мастера"]


#проверка на вверный формат ввода даты
def check_date_format(date_string):
    # Паттерн для проверки формата даты: yyyy-mm-dd
    pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')

    # Проверка совпадения введенной строки с паттерном
    if re.match(pattern, date_string):
        return True
    else:
        return False

def validate_time_format(time_str):
    # Паттерн для проверки времени в формате "часы:минуты"
    time_str = time_str.split(" ")
    time_pattern = re.compile(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')

    test = True
    print(time_str)
    # Проверяем соответствие введенного времени паттерну
    for i in time_str:
        if time_pattern.match(i):
            pass
        else:
            test = False
    return test


def main_func():    
    @bot.message_handler(commands=['start'])
    def start(message):
        global admins

        message_id = message.chat.id
        name_mes = message.from_user.first_name
        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton("Услуги")
        btn2 = types.KeyboardButton("Мои записи")
        btn3 = types.KeyboardButton("Добавить администратора")
        btn4 = types.KeyboardButton("Удалить свою запись")
        btn5 = types.KeyboardButton("Просмотр записей мастера")
        btn6 = types.KeyboardButton("Добавление свободной записи")
        btn7 = types.KeyboardButton("Добавление/Удаление услуги")
        btn8 = types.KeyboardButton("Добавление/Удаление мастера")

        conn = sqlite3.connect(r'salon_krasoti.db')
        cur = conn.cursor()
        cur.execute(f"select * from 'Администраторы' where admin_user_id = {message_id};")
        admins = cur.fetchall()

        if len(admins) == 0:
            markup.row(btn1, btn2, btn4)
        else:
            markup.row(btn1, btn2, btn3, btn4)
            markup.row(btn5, btn6, btn7, btn8)
        bot.send_message(message_id, f'Здравствуйте, {name_mes}, нажмите на кнопку "Услуги", чтобы начать запись. Кнопка "Мои записи", чтобы увидеть свои записи, если они у вас есть. Кнопка "Удалить свою запись", чтобы удалить свою запись, если она у вас есть.', reply_markup=markup, parse_mode='HTML')
        bot.send_message(message_id,
                         f'Все услуги данного салона:')

        cur.execute('''select название from Услуги group by название;''')
        ysl_vivod = cur.fetchall()

        info_vivod = ''
        for el in ysl_vivod:
            info_vivod += f'<b>{el[0].upper()}</b>\n'
            cur.execute('''select детальные_услуги.название , цена from детальные_услуги
                            inner join Услуги on Услуги.id = детальные_услуги.id_услуги
                            where Услуги.название = ?;''', (el[0],))
            ysl_vivod1 = cur.fetchall()
            for el1 in ysl_vivod1:
                info_vivod += f'• {el1[0]}'
                info_vivod += f' {el1[1]}\n'

        bot.send_message(message_id, info_vivod.format(message.from_user), parse_mode="HTML")

    @bot.message_handler(content_types=['text'])
    def uslygi(message):
        global delete_master_m
        global step
        global admins
        global watch
        global add_zapis
        global del_your_zap
        global delete_ys
        #вывод услуг для записи клинта
        if message.text == "Услуги":
            global yslyga, master_r, date_t, time_t
            yslyga, master_r, date_t, time_t = None, None, None, None
            conn = sqlite3.connect(r'salon_krasoti.db')
            cur = conn.cursor()
            cur.execute("Select мастер_id from Свободные_записи group by мастер_id;")
            users = cur.fetchall()
            markup = types.InlineKeyboardMarkup()

            if len(users) == 0:
                bot.send_message(message.chat.id, "Нет свободных мастеров и записей!".format(message.from_user), parse_mode="HTML")
            else:
                cur.execute(f'''select Услуги.название from Свободные_записи
                                inner join Услуги on Услуги.id = Свободные_записи.услуга_id
                                where Услуги.id = Свободные_записи.услуга_id
                                group by Услуги.название ;''')
                users1 = cur.fetchall()
                for el1 in users1:
                    button1 = types.InlineKeyboardButton(f"{el1[0]}", callback_data=(el1[0]))
                    markup.add(button1)

                bot.send_message(message.chat.id, "Услуги".format(message.from_user), parse_mode="HTML",
                                 reply_markup=markup)
                step = 1
                watch, add_zapis, del_your_zap = 0, 0, 0
            cur.close()
            conn.close()

        #вывод записей пользователя
        if message.text == "Мои записи":
            conn = sqlite3.connect(r'salon_krasoti.db')
            cur = conn.cursor()
            cur.execute(f'''
            select Клиенты.ФИО, Записи.дата, Записи.время, Мастера.ФИО, Мастера.специализация from Записи 
            INNER join Клиенты on Клиенты.id = Записи.клиент_id
            INNER join Мастера on Мастера.id = Записи.мастер_id
            where Клиенты.telegram_id = {message.chat.id} group by Клиенты.ФИО;
            ''')
            zapisi = cur.fetchall()
            if len(zapisi) != 0:
                for el in zapisi:
                    bot.send_message(message.chat.id,
                                     f"Фио: {el[0]}\nДата: {el[1]}\nВремя: {el[2]}\nУслуга: {el[4]}\nМастер: {el[3]}")
            else:
                bot.send_message(message.chat.id,"У вас нет записей")
            conn.commit()
            cur.close()
            conn.close()

        #добавление администратора
        if message.text == "Добавить администратора":
            conn = sqlite3.connect(r'salon_krasoti.db')
            cur = conn.cursor()
            cur.execute(f"select * from 'Администраторы' where admin_user_id = {message.chat.id};")
            admins = cur.fetchall()
            
            if len(admins) != 0:
                bot.send_message(message.chat.id,"Напишите user_id нового администратора")
                bot.register_next_step_handler(message, AddAdminsId)
            
            cur.close()
            conn.close()    
        #удаление клиентом своей записи
        if message.text == "Удалить свою запись":
            
            conn = sqlite3.connect(r'salon_krasoti.db')
            cur = conn.cursor()
            cur.execute(f'''
                        select Клиенты.ФИО, Записи.дата, Записи.время, Мастера.ФИО, Мастера.специализация from Записи
                        INNER join Клиенты on Клиенты.id = Записи.клиент_id
                        INNER join Мастера on Мастера.id = Записи.мастер_id
                        where Клиенты.telegram_id = {message.chat.id};
                        ''')
            zapisi = cur.fetchall()
            markup = types.InlineKeyboardMarkup()

            if len(zapisi) != 0:
                i = 1
                for el in zapisi:
                    bot.send_message(message.chat.id,
                                f"Запись №{i}\nФио: <code>{el[0]}</code>\nДата: <code>{el[1]}</code>\nВремя: <code>{el[2]}</code>\nУслуга: <code>{el[4]}</code>\nМастер: <code>{el[3]}</code>".format(message.from_user),
                                parse_mode="HTML")
                    i = i + 1

                for el in range(len(zapisi)):
                    button1 = types.InlineKeyboardButton(f"Удалить запись №{el + 1}", callback_data=f'{zapisi[el][1]},{zapisi[el][2]},{zapisi[el][3]}')
                    markup.add(button1)
                bot.send_message(message.chat.id,
                                 f"Выберите запись, которую хотите удалить.".format(
                                     message.from_user),
                                 parse_mode="HTML",
                                 reply_markup=markup)
                del_your_zap = 1
                step, watch, add_zapis = 0, 0, 0
            else:
                bot.send_message(message.chat.id, "У вас нет записей")

            conn.commit()
            cur.close()
            conn.close()

        #для админа! просомтр записей у мастера
        if message.text == 'Просмотр записей мастера':
            # global master_r
            # master_r = None
            conn = sqlite3.connect(r'salon_krasoti.db')
            cur = conn.cursor()
            cur.execute('''select ФИО from Мастера;''')
            qwerty = cur.fetchall()
            markup = types.InlineKeyboardMarkup()

            for el in qwerty:
                button_watch = types.InlineKeyboardButton(f"{el[0]}", callback_data=(el[0]))
                markup.add(button_watch)

            bot.send_message(message.chat.id, "Мастера. Выберете кто вас интересует.".format(message.from_user), parse_mode="HTML", reply_markup=markup)

            watch = 1
            step, delete_master_m, add_zapis, del_your_zap, delete_ys = 0, 0, 0, 0, 0
            cur.close()
            conn.close()

        #добавлеине свободной записи у мастера ( выбор мастера )
        if message.text == 'Добавление свободной записи':
            conn = sqlite3.connect(r'salon_krasoti.db')
            cur = conn.cursor()
            cur.execute('''select ФИО from Мастера;''')
            add_master = cur.fetchall()
            markup = types.InlineKeyboardMarkup()

            for el in add_master:
                button_watch = types.InlineKeyboardButton(f"{el[0]}", callback_data=(el[0]))
                markup.add(button_watch)

            bot.send_message(message.chat.id, "Выберите мастера у которого хотите добавить запись(и).".format(message.from_user), parse_mode="HTML", reply_markup=markup)

            add_zapis = 1
            watch,step, delete_master_m, del_your_zap, delete_ys = 0, 0, 0, 0, 0
            
            cur.close()
            conn.close()

        #добавление/удаление услуги
        if message.text == 'Добавление/Удаление услуги':
            markup = types.InlineKeyboardMarkup()
            button_Add_yslyga = types.InlineKeyboardButton(f"Добавить новую услугу.", callback_data=('Add yslyga'))
            button_Delete_yslyga = types.InlineKeyboardButton(f"Удалить услугу.", callback_data=('Delete yslyga'))
            button_Delete_det_yslyga = types.InlineKeyboardButton(f"Удалить описание услугу.", callback_data=('Delete det yslyga'))
            markup.add(button_Add_yslyga)
            markup.add(button_Delete_yslyga)
            markup.add(button_Delete_det_yslyga)
            bot.send_message(message.chat.id, 'Что вы хотите сделать? (Выберите нажав кнопку ниже).'.format(message.from_user), parse_mode="HTML", reply_markup=markup)
            watch,step, delete_master_m,add_zapis, del_your_zap, delete_ys = 0, 0, 0, 0, 0, 0

        # добавление/удаление мастера
        if message.text == 'Добавление/Удаление мастера':
            markup = types.InlineKeyboardMarkup()
            button_Add_yslyga = types.InlineKeyboardButton(f"Добавить нового мастера.", callback_data=('Add master'))
            button_Delete_yslyga = types.InlineKeyboardButton(f"Удалить мастера.", callback_data=('Delete master'))
            markup.add(button_Add_yslyga, button_Delete_yslyga)
            bot.send_message(message.chat.id,
                             'Что вы хотите сделать? (Выберите нажав кнопку ниже).'.format(message.from_user),
                             parse_mode="HTML", reply_markup=markup)
            watch,step, delete_master_m,add_zapis, del_your_zap, delete_ys = 0, 0, 0, 0, 0, 0


    #функция для добавления администратора
    def AddAdminsId(message):
        if message.text not in mas_commands:
            global id_admin
            id_admin = message.text
    
    
            bot.send_message(message.chat.id,"Напишите ФИО нового администратора")
            bot.register_next_step_handler(message, AddAdminsFio)
        else:
            bot.send_message(message.chat.id,"Выберите необходимую вам команду снова.")
    #функция 2 для добавления администратора
    def AddAdminsFio(message):
        if message.text not in mas_commands:
            global Fio_admin
            Fio_admin = message.text
    
    
            conn = sqlite3.connect(r'salon_krasoti.db')
            cur = conn.cursor()
            cur.execute(f"Insert into Администраторы (admin_user_id, ФИО) values ('{id_admin}', '{Fio_admin}');")
    
            conn.commit()
            cur.close()
            conn.close()
    
            bot.send_message(message.chat.id,f"Успешно зарегистрирован новый администратор.\nФИО: {Fio_admin}.\nUser_id {id_admin}.")
        else:
            bot.send_message(message.chat.id,"Выберите необходимую вам команду снова.")


    yslyga = None
    time_t = None
    master_r = 0


    name_del_yslyga = None
    delete_ys = 0
    

    add_mew_master = 0
    special = None

    @bot.callback_query_handler(func=lambda callback: True)
    def callback(callback):
        if callback.data not in mas_commands:
            message_id = callback.message.chat.id
            #bot.send_message(chat_id=callback.message.chat.id, text=f"{callback.data}")
            global date_t
            global step
            global time_t
            global vblbor_time
            global master_r
            global watch
            global add_zapis
            global delete_ys
            global delete_master_m
            global add_new_master

            global delete_mas_name
    
            global del_your_zap
            global mas_znach_na_ydalenie

            global add_yslyga_obsh

            global check_on_zapis
            global name_yslyga
            conn = sqlite3.connect(r'salon_krasoti.db')
            cur = conn.cursor()
            markup = types.InlineKeyboardMarkup()
    
            if(callback.data[0]=="+"):
                mas_check_zap = str(callback.data).split(',')
                for i in mas_check_zap:
                    print(i)
                cur.executescript(f'''
                UPDATE Записи
                SET запись_подтверждена = 1
                WHERE EXISTS (
                    SELECT 1
                    FROM Мастера
                    WHERE Мастера.id = Записи.мастер_id
                    AND Мастера.ФИО = '{mas_check_zap[3]}'
                    AND Записи.дата = '{mas_check_zap[1]}'
                    AND Записи.время = '{mas_check_zap[2]}'
                );
                ''')
                conn.commit()
                bot.delete_message(callback.message.chat.id, callback.message.message_id - 0)
                bot.send_message(callback.message.chat.id,
                                 f"✅Запись успешно подтвержденна.".format(
                                     callback.message.from_user),
                                 parse_mode="HTML", reply_markup=markup)

                
            
            if del_your_zap == 1:
                bot.delete_message(callback.message.chat.id, callback.message.message_id - 0)
                mas_znach_na_ydalenie = str(callback.data).split(',')
    
                cur.executescript('''INSERT INTO Свободные_записи(услуга_id,мастер_id, дата, время)
                                                SELECT Записи.услуга_id, Записи.мастер_id, Записи.дата, Записи.время
                                                FROM Записи
                                                inner join Мастера on Мастера.id = Записи.мастер_id
                                                 WHERE Мастера.ФИО='%s' and Записи.дата ='%s' and Записи.время ='%s';''' % (
                mas_znach_na_ydalenie[2], mas_znach_na_ydalenie[0], mas_znach_na_ydalenie[1]))
    
    
                cur.executescript('''DELETE FROM Записи
                                            WHERE id IN (
                                            SELECT Записи.id
                                            FROM Записи
                                            INNER JOIN Мастера ON Мастера.id = Записи.мастер_id
                                            WHERE Мастера.ФИО = '%s'
                                            AND Записи.дата = '%s'
                                            AND Записи.время = '%s'
                                            );''' % (mas_znach_na_ydalenie[2], mas_znach_na_ydalenie[0], mas_znach_na_ydalenie[1]))
                conn.commit()
                bot.send_message(callback.message.chat.id, f"Успешно удалена запись!\nДата: {mas_znach_na_ydalenie[2]}\nВремя: {mas_znach_na_ydalenie[0]}\nМастер: {mas_znach_na_ydalenie[1]}.".format(callback.message.from_user),
                                 parse_mode="HTML", reply_markup=markup)
                del_your_zap = 0
                master_r, delete_ys, add_new_master, step, add_zapis = 0,0, 0, 0,0
            #добавление нового мастера
            if callback.data == 'Add master':
                bot.send_message(message_id, 'Введите ФИО нового мастера.')
                bot.register_next_step_handler(callback.message, add_master_new)
    
            #добавлеине нового мастера в бд
            if add_new_master == 1:
                global special
                special = callback.data
                global new_master
                conn = sqlite3.connect(r'salon_krasoti.db')
                cur = conn.cursor()
    
                cur.execute(f'''INSERT INTO Мастера(ФИО, специализация) values("{new_master}","{special}");''')
                conn.commit()
                bot.send_message(callback.message.chat.id, f'Успешно добавлен новый мастер: {new_master}.\n Специализирующийся на {special}.')
                add_new_master = 0
                master_r, delete_ys, step, add_zapis, del_your_zap = 0, 0, 0, 0, 0
    
            #удаление мастера
            if callback.data == 'Delete master':
                conn = sqlite3.connect(r'salon_krasoti.db')
                cur = conn.cursor()
                cur.execute('''select ФИО from Мастера;''')
                delete_yslyga_m = cur.fetchall()
                markup = types.InlineKeyboardMarkup()
    
                for el in delete_yslyga_m:
                    delete_but_m = types.InlineKeyboardButton(f"{el[0]}", callback_data=(el[0]))
                    markup.add(delete_but_m)
    
                bot.send_message(callback.message.chat.id,
                                 "Выберите мастера которого хотите удалить.".format(callback.message.from_user),
                                 parse_mode="HTML", reply_markup=markup)
    
                delete_master_m = 1
                master_r, delete_ys, add_new_master, step, add_zapis, del_your_zap = 0, 0, 0, 0, 0, 0
            elif delete_master_m == 1:
                delete_mas_name = callback.data
    
                conn = sqlite3.connect(r'salon_krasoti.db')
                cur = conn.cursor()
    
                cur.execute(f'''delete from Мастера where Мастера.ФИО = "{delete_mas_name}";''')
                conn.commit()
    
                bot.send_message(callback.message.chat.id, f"Успешно удален мастер: {delete_mas_name}.".format(callback.message.from_user),
                                 parse_mode="HTML", reply_markup=markup)
                delete_master_m = 0
    
            #добваление новой услуги
            if callback.data == 'Add yslyga':
                markup = types.InlineKeyboardMarkup()
                conn = sqlite3.connect(r'salon_krasoti.db')
                cur = conn.cursor()
                cur.execute('''select название from Услуги;''')
                yslygiiii = cur.fetchall()
                global test_mas
                test_mas = []
                for el in yslygiiii:
                    button1 = types.InlineKeyboardButton(f"{el[0]}", callback_data=(el[0]))
                    markup.add(button1)
                    test_mas.append(str(el[0]))
                button1 = types.InlineKeyboardButton(f"Добавить новое название услуги.", callback_data=('Add_yslyga_new_name'))
                markup.add(button1)

                bot.send_message(message_id, 'Выберите услугу или добавьте новую.', reply_markup=markup)
                global add_yslyga_obsh
                
                add_yslyga_obsh = 1


            
            
            if callback.data == "Add_yslyga_new_name":
                bot.send_message(message_id, 'Напишите название новой услуги.', reply_markup=markup)
                bot.register_next_step_handler(callback.message, add_yslygaa)


            if add_yslyga_obsh == 1 and str(callback.data) in test_mas:
                global name_yslyga
                name_yslyga = callback.data
                bot.send_message(message_id, 'Введите описание.')
                bot.register_next_step_handler(callback.message, add_yslyga1)
                
                

            #удаление детальных услуг 
            if callback.data == 'Delete det yslyga':
                conn = sqlite3.connect(r'salon_krasoti.db')
                cur = conn.cursor()
#                 cur.execute('''select Услуги.название,детальные_услуги.название,детальные_услуги.цена from детальные_услуги
# inner join Услуги on Услуги.id = детальные_услуги.id_услуги;''')
#                 Delete_yslyga_det = cur.fetchall()
#
#                 test = ""
#                 for i in range(len(Delete_yslyga_det)) :
#                     test += f"Запись №{i+1}\nОсновная услуга:{Delete_yslyga_det[i][0]}\nНазвание:<b><code>{Delete_yslyga_det[i][1]}</code></b>\nЦена:{Delete_yslyga_det[i][2]}\n"
#                 bot.send_message(callback.message.chat.id,test, parse_mode="HTML")

                cur.execute('''select название from Услуги group by название;''')
                ysl_vivod = cur.fetchall()

                info_vivod = ''
                for el in ysl_vivod:
                    i = 0
                    info_vivod += f'<b>{el[0].upper()}</b>\n'
                    cur.execute('''select детальные_услуги.название , цена from детальные_услуги
                                     inner join Услуги on Услуги.id = детальные_услуги.id_услуги
                                     where Услуги.название = ?;''', (el[0],))
                    ysl_vivod1 = cur.fetchall()
                    for el1 in ysl_vivod1:
                        i += 1
                        info_vivod += f'{i}) <code>{el1[0]}</code>'
                        info_vivod += f' {el1[1]}\n'

                bot.send_message(message_id, info_vivod.format(callback.message.from_user), parse_mode="HTML")
                
                
    
                bot.send_message(callback.message.chat.id,"Напишите название услуги которую вы хотите удалить(можно скопировать нажав на текст)")
                bot.register_next_step_handler(callback.message, delete_ys_det)

        
    

            #удаление услуги
            if callback.data == 'Delete yslyga':
                conn = sqlite3.connect(r'salon_krasoti.db')
                cur = conn.cursor()
                cur.execute('''select название from Услуги;''')
                Delete_yslyga = cur.fetchall()
                markup = types.InlineKeyboardMarkup()
                
                for el in Delete_yslyga:
                    delete_but = types.InlineKeyboardButton(f"{el[0]}", callback_data=(el[0]))
                    markup.add(delete_but)
    
                bot.send_message(callback.message.chat.id,
                                 "Выберите услугу которую хотите удалить.".format(callback.message.from_user),
                                 parse_mode="HTML", reply_markup=markup)
                
                delete_ys = 1
                master_r, add_new_master, step, add_zapis, del_your_zap = 0,0,0,0,0
            # удаление услуги (получение ее названия и удаления из бд)
            elif delete_ys == 1:
                global name_del_yslyga
                name_del_yslyga = callback.data
    
                conn = sqlite3.connect(r'salon_krasoti.db')
                cur = conn.cursor()
                    
                cur.execute(f'''delete from детальные_услуги 
                                where id_услуги in ( select id from Услуги where Услуги.название = "{name_del_yslyga}");''')
                conn.commit()
                
                cur.execute(f'''delete from Услуги where Услуги.название = "{name_del_yslyga}";''')
                conn.commit()
                
                
                bot.send_message(callback.message.chat.id, f'Успешно удалена основная услуга <b>{name_del_yslyga}</b> и её детальные услуги', parse_mode="HTML")
    
                delete_ys = 0
                
    
    
            #добавлеине свободной записи у мастера 1 ( выбор услуги )
            if add_zapis == 1:
                global add_zapis_master
                add_zapis_master = callback.data
    
                conn = sqlite3.connect(r'salon_krasoti.db')
                cur = conn.cursor()
                cur.execute('''select название from Услуги;''')
                add_master = cur.fetchall()
                markup = types.InlineKeyboardMarkup()
    
                for el in add_master:
                    button_watch = types.InlineKeyboardButton(f"{el[0]}", callback_data=(el[0]))
                    markup.add(button_watch)
    
                bot.send_message(callback.message.chat.id, "Выберите услугу которую мастер будет предоставлять.".format(callback.message.from_user), parse_mode="HTML", reply_markup=markup)
    
                add_zapis = 2
                master_r, delete_ys, add_new_master, step, del_your_zap = 0,0,0,0,0
    
            #добавлеине свободной записи у мастера 2 ( выбор даты )
            elif add_zapis == 2:
                add_zapis = 0
                global add_zapis_yslyga
                add_zapis_yslyga = callback.data
    
                bot.send_message(callback.message.chat.id, "Введите дату на которую хотите добавить запись у мастера (в формате (год-месяц-день) 2000-12-30).")
                bot.register_next_step_handler(callback.message, add_zapis_next)
    
            #просмотр записей у мастера
            if watch == 1:
                bot.delete_message(callback.message.chat.id, callback.message.message_id - 0)
                master_r = None
                global watch_m
                watch_m = callback.data
    
                cur.execute(f'''select Свободные_записи.дата, Свободные_записи.время from Свободные_записи join Мастера on мастер_id = Мастера.id where Мастера.ФИО = '{watch_m}' order by Свободные_записи.дата, Свободные_записи.время;''')
                watch_m1 = cur.fetchall()
    
                i = 1
                info = ''
                if len(watch_m1) != 0:
                    info += f'<b>Свободные записи</b>\nМастер: {watch_m}\nЗапись | Дата | Время\n'
                    for el in watch_m1:
                        info += f'{i} | {el[0]} | {el[1]}.\n'
                        i += 1
                else:
                    info = f'У {watch_m}, нет свободных записей.'
    
                bot.send_message(callback.message.chat.id, info, parse_mode="HTML")
    
                cur.execute(f'''select Записи.дата, Записи.время from Записи
                                join Мастера on Записи.мастер_id = Мастера.id
                                join Услуги on Записи.услуга_id = Услуги.id
                                where Мастера.ФИО = '{watch_m}'
                                order by Записи.дата, Записи.время;''')
                watch_m2 = cur.fetchall()
    
                i = 1
                info1 = ''
                if len(watch_m2) != 0:
                    info1 += f'<b>Записи</b>\nМастер: {watch_m}\nЗапись | Дата | Время\n'
                    for el in watch_m2:
                        info1 += f'{i} | {el[0]} | {el[1]}.\n'
                        i += 1
                else:
                    info1 = f'У {watch_m}, нет записей.'
    
                bot.send_message(callback.message.chat.id, info1, parse_mode="HTML")
    
                watch = 0
    
            #начало записи у клиенат
            #выводит мастеров
            if step == 1:
                bot.delete_message(callback.message.chat.id, callback.message.message_id - 0)
                master_r = None
                global yslyga
                yslyga = callback.data
                cur.execute('''SELECT Мастера.ФИО FROM Свободные_записи
                                Inner join Услуги on Услуги.id = Свободные_записи.услуга_id
                                Inner join Мастера on Мастера.id = Свободные_записи.мастер_id
                                WHERE Услуги.название = '%s' GROUP by Мастера.ФИО ;''' % (yslyga))
                spec = cur.fetchall()
                for el in spec:
                    button1 = types.InlineKeyboardButton(f"Мастер : {el[0]}.", callback_data=(el[0]))
                    markup.add(button1)
    
                bot.send_message(callback.message.chat.id, f"Выберите мастера {yslyga} : ".format(callback.message.from_user), parse_mode="HTML", reply_markup=markup)
                step = 2
                master_r, delete_ys, add_new_master, add_zapis, del_your_zap = 0, 0, 0, 0, 0
            #выводит свободные даты для записи
            elif step == 2 or callback.data == master_r:
                bot.delete_message(callback.message.chat.id, callback.message.message_id - 0)
                master_r = callback.data
                cur.execute(f'''select Свободные_записи.дата from Свободные_записи 
                                INNER JOIN Мастера ON Мастера.id = Свободные_записи.мастер_id 
                                INNER JOIN Услуги ON Услуги.id = Свободные_записи.услуга_id 
                                where Мастера.ФИО = '{master_r}' and  Услуги.название = '{yslyga}'
                                group by Свободные_записи.дата;''')
                svobod_zapisi = cur.fetchall()
                info = ''
                for el in svobod_zapisi:
                    button1 = types.InlineKeyboardButton(f"Свободная дата : {el[0]}.", callback_data=(el[0]))
                    markup.add(button1)
    
                bot.send_message(callback.message.chat.id, f"Выберите дату на {yslyga} у мастера {master_r}: ".format(callback.message.from_user), parse_mode="HTML", reply_markup=markup)
                bot.send_message(callback.message.chat.id, f"Если хотите выбрать другую услугу или мастера, нажмите снова кнопку Услуги, для начала новой записи. ".format(callback.message.from_user), parse_mode="HTML")
                step = 3
                delete_ys, add_new_master, add_zapis, del_your_zap = 0,0,0,0
            #выводит свободное время для записи
            elif step == 3:
                bot.delete_message(callback.message.chat.id, callback.message.message_id - 0)
                bot.delete_message(callback.message.chat.id, callback.message.message_id + 1)
                date_t = callback.data
                # cur.execute(f'''select Свободные_записи.время from Свободные_записи INNER JOIN Мастера ON Мастера.id = Свободные_записи.мастер_id  where Мастера.ФИО = '{master_r}' and Свободные_записи.дата = '{date_t}';''')
                cur.execute(f'''select Свободные_записи.время from Свободные_записи
                                INNER JOIN Мастера ON Мастера.id = Свободные_записи.мастер_id
                                INNER JOIN Услуги ON Услуги.id = Свободные_записи.услуга_id
                                where Мастера.ФИО = '{master_r}' and Свободные_записи.дата = '{date_t}' and Услуги.название = '{yslyga}';''')
                svobod_zapisi = cur.fetchall()

                info = ''
                for el in svobod_zapisi:
                    button1 = types.InlineKeyboardButton(f"Свободное время : {el[0]}.", callback_data=(el[0]))
                    markup.add(button1)
    
                button2 = types.InlineKeyboardButton(f"Хочу выбрать другую дату.", callback_data=(master_r))
                markup.add(button2)
    
                bot.send_message(callback.message.chat.id, "Выберите время : ".format(callback.message.from_user), parse_mode="HTML", reply_markup=markup)
                step = 4
                delete_ys, add_new_master, add_zapis, del_your_zap = 0,0,0,0
            #окончательная регистрация переходит к дургим функциям
            elif step == 4:
                bot.delete_message(callback.message.chat.id, callback.message.message_id - 0)
                time_t = callback.data
                bot.send_message(callback.message.chat.id,
                                 "Для окончательной регистрации, нам потребуется ваше ФИО и номер телефона для обратной связи. В ответ напишите сейчас ваше <b>ФИО</b>, в формате (Иванов Иван).".format(
                                     callback.message.from_user),
                                 parse_mode="HTML")
                
                bot.register_next_step_handler(callback.message, EndOfZapic1)
                delete_ys, add_new_master, step, add_zapis, del_your_zap = 0,0,0,0,0
            cur.close()
            conn.close()

    # добваление новой услуги (сохранение навзания услуги и запрос описания)
    def delete_ys_det(message):
        if message.text not in mas_commands:
            global name_del_yslyga_det
            name_del_yslyga_det = message.text

            conn = sqlite3.connect(r'salon_krasoti.db')
            cur = conn.cursor()

            cur.execute(f'''delete from детальные_услуги where детальные_услуги.название = "{name_del_yslyga_det}";''')
            conn.commit()
            bot.send_message(message.chat.id, f'Успешно удалена детальная услуга <b>{name_del_yslyga_det}</b>', parse_mode="HTML")
        else:
            bot.send_message(message.chat.id, "Выберите необходимую вам команду снова.")
    def add_yslygaa(message):
        global add_yslyga_obsh
        add_yslyga_obsh = 0
        if message.text not in mas_commands:
            global name_yslyga
            name_yslyga = message.text

            conn = sqlite3.connect(r'salon_krasoti.db')
            cur = conn.cursor()
            cur.execute(f'''insert into Услуги(название)
            select "{name_yslyga}"
            WHERE NOT EXISTS (
            SELECT 1 FROM Услуги WHERE название = '{name_yslyga}'
            );''')
            conn.commit()
            cur.close()
            conn.close()
            bot.send_message(message.chat.id, f"Вы добавили новую услугу с названием {name_yslyga}.")
        else:
            bot.send_message(message.chat.id, "Выберите необходимую вам команду снова.")

    # добваление новой услуги (сохранение краткого описания услуги и запрос цены)
    opisanie_yslyga = None

    def add_yslyga1(message):
        global add_yslyga_obsh
        add_yslyga_obsh = 0
        if message.text not in mas_commands:
            global opisanie_yslyga
            opisanie_yslyga = message.text
            bot.send_message(message.chat.id, 'Введите цену данной услуги.')
            bot.register_next_step_handler(message, add_yslyga2)
        else:
            bot.send_message(message.chat.id, "Выберите необходимую вам команду снова.")
    # добваление новой услуги (сохранение цены услуги и ее добавлеине в бд)
    cena_yslyga = None

    def add_yslyga2(message):
        if message.text not in mas_commands:
            global name_yslyga
            global opisanie_yslyga
            global cena_yslyga
            cena_yslyga = message.text

            

            conn = sqlite3.connect(r'salon_krasoti.db')
            cur = conn.cursor()

            cur.execute(
                f'''insert into детальные_услуги(id_услуги,название, цена)
                    select Услуги.id, "{opisanie_yslyga}", "{cena_yslyga}"
                    from Услуги
                    WHERE Услуги.название = '{name_yslyga}' and NOT EXISTS (
                    SELECT 1 FROM детальные_услуги WHERE название = '{name_yslyga}'
                    );''')
            conn.commit()

            bot.send_message(message.chat.id, f"Успешно добавлена новая услуга!\nНазвание услуги: <b>{name_yslyga}</b>.\nЦена: <b>{cena_yslyga}</b>.", parse_mode="HTML")

            cur.close()
            conn.close()
        else:
            bot.send_message(message.chat.id,"Выберите необходимую вам команду снова.")

    #добавление нового мастера (получение ФИО и запрос услуги)
    new_master = None
    def add_master_new(message):
        if message.text not in mas_commands:
            global add_new_master
            global new_master
            new_master = message.text
            conn = sqlite3.connect(r'salon_krasoti.db')
            cur = conn.cursor()
            cur.execute('''select название from Услуги;''')
            new_yslyga_c = cur.fetchall()
            markup = types.InlineKeyboardMarkup()
    
            for el in new_yslyga_c:
                add_but_m = types.InlineKeyboardButton(f"{el[0]}", callback_data=(el[0]))
                markup.add(add_but_m)
    
            bot.send_message(message.chat.id,
                             "Выберите услугу которую мастер будет предоставлять.".format(message.from_user),
                             parse_mode="HTML", reply_markup=markup)
            add_new_master = 1
    
    
            cur.close()
            conn.close()
        else:
            bot.send_message(message.chat.id,"Выберите необходимую вам команду снова.")
    #удаление услуги (получение ее названия и удаления из бд)
    name_del_yslyga = None


    global add_zapis_cikle
    # добавлеине свободной записи у мастера 3 ( выбор времени )
    def add_zapis_next(message):
        if message.text not in mas_commands:
            global add_zapis_data
            add_zapis_data = message.text.strip()
    
            if check_date_format(add_zapis_data):
                bot.send_message(message.chat.id,
                                 'Введите время в формате (11:00 12:00 13:00 ...)')
                bot.register_next_step_handler(message, add_zapis_next_2)
            else:
                bot.send_message(message.chat.id,
                                 '❌Неправильный формат даты. Формат должен быть -> (год-месяц-день) 2000-12-30')
                bot.register_next_step_handler(message, add_zapis_next)
        else:
            bot.send_message(message.chat.id,"Выберите необходимую вам команду снова.")
    # добавлеине свободной записи у мастера 4
    def add_zapis_next_2(message):
        if message.text not in mas_commands:
            global add_zapis_time
            global add_zapis_data
            global add_zapis_yslyga
            global add_zapis_master
            add_zapis_time = message.text
            # add_zapis_time = add_zapis_time.split()
            if validate_time_format(add_zapis_time):
                add_zapis_time = add_zapis_time.split()
                conn = sqlite3.connect(r'salon_krasoti.db')
                cur = conn.cursor()

                for i in range(len(add_zapis_time)):

                    cur.execute(f'''INSERT INTO Свободные_записи(услуга_id, мастер_id, дата, время)
                                SELECT Услуги.id, Мастера.id, "{add_zapis_data}", "{add_zapis_time[i]}"
                                FROM Мастера
                                JOIN Услуги ON Услуги.название = "{add_zapis_yslyga}"
                                WHERE Мастера.ФИО = "{add_zapis_master}"
                                AND NOT EXISTS (
                                    SELECT 1 
                                    FROM Свободные_записи 
                                    WHERE Свободные_записи.услуга_id = Услуги.id 
                                    AND Свободные_записи.мастер_id = Мастера.id 
                                    AND Свободные_записи.дата = "{add_zapis_data}" 
                                    AND Свободные_записи.время = "{add_zapis_time[i]}"
                                );''')

                    conn.commit()
                cur.close()
                conn.close()
                bot.send_message(message.chat.id, f'Успешно добавлена свободная запись.\nМастер: {add_zapis_master}.\nДата: {add_zapis_data}.\nВремя: {add_zapis_time}.'.format(message.from_user),
                                 parse_mode="HTML")
            else:
                bot.send_message(message.chat.id,
                                 '❌Неправильный формат времени. Формат должен быть -> 10:00 11:00 ...')
                bot.register_next_step_handler(message, add_zapis_next_2)
        else:
            bot.send_message(message.chat.id,"Выберите необходимую вам команду снова.")

    # name_klient = None
    telephone_klient = None


    date_d = None
    time_d = None
    master_d = None

    #окончательная запись 1
    def EndOfZapic1(message):
        if message.text not in mas_commands:
            global name_klient
            name_klient = message.text
            bot.send_message(message.chat.id,
                             "И введите свой номер телефона.".format(
                                 message.from_user),
                             parse_mode="HTML")
            
            bot.register_next_step_handler(message, EndOfZapic3)
        else: 
            bot.send_message(message.chat.id,"Выберите необходимую вам команду снова.")
    #окончательная запись 2
    def EndOfZapic3(message):
        if message.text not in mas_commands:
            message_id = message.chat.id
            global date_t
            global step
            global time_t
            global telephone_klient
            global master_r
            global yslyga
    
            telephone_klient = message.text
            conn = sqlite3.connect(r'salon_krasoti.db')
            cur = conn.cursor()
    
            # vblbor_time = callback.data.message
            cur.execute("INSERT INTO Клиенты (telegram_id, ФИО, номер_телефона) VALUES ('%s', '%s', '%s');" % (message_id, name_klient, telephone_klient))
            cur.execute(f'''select id from Клиенты
                            where ФИО = '{name_klient}'
                            ORDER BY id DESC
                            limit 1;''')
            id_klient = cur.fetchall()
            cur.executescript(f'''INSERT INTO Записи(клиент_id,услуга_id,мастер_id,дата,время, запись_подтверждена)
    select Клиенты.id, Свободные_записи.услуга_id, Свободные_записи.мастер_id, Свободные_записи.дата, Свободные_записи.время, 1
    from Свободные_записи
    INNER JOIN Мастера ON Мастера.id = Свободные_записи.мастер_id
    INNER JOIN Клиенты ON Клиенты.telegram_id = '{message_id}'
    WHERE Мастера.ФИО='{master_r}' AND Свободные_записи.дата ='{date_t}' AND Свободные_записи.время ='{time_t}' and Клиенты.id = '{id_klient[0][0]}'
    AND NOT EXISTS (
    SELECT 1
    FROM Записи
    WHERE Записи.услуга_id = Свободные_записи.услуга_id
    AND Записи.мастер_id = Свободные_записи.мастер_id
    AND Записи.дата = Свободные_записи.дата
    AND Записи.время = Свободные_записи.время);
                                    ''')
    
            cur.executescript('''DELETE FROM Свободные_записи
                        WHERE id IN (
                        SELECT Свободные_записи.id
                        FROM Свободные_записи
                        INNER JOIN Мастера ON Мастера.id = Свободные_записи.мастер_id
                        WHERE Мастера.ФИО = '%s'
                        AND Свободные_записи.дата = '%s'
                        AND Свободные_записи.время = '%s'
                        );''' % (master_r, date_t, time_t))
            conn.commit()

            bot.send_message(message.chat.id, f"✅Запись прошла успешно.\nДата: {date_t} \nВремя: {time_t}\nФио: {name_klient}\nМастер: {master_r}\nУслуга: {yslyga}.\n❗️В 18:00 - за день до записи, вам придет запрос на её подтверждение, если он не пришло, она подтвердилось автоматически.".format(message.from_user),
                             parse_mode="HTML")

            cur.execute('''select admin_user_id from Администраторы;''')
            adminis = cur.fetchall()

            for el in adminis:
                bot.send_message(el[0], f"Появилась новая запись\nКлиент: {name_klient} \nДата: {date_t} \nВремя: {time_t}\nМастер: {master_r}\nУслуга: {yslyga}\n")
            step = 0
    
            cur.close()
            conn.close()
        else: 
            bot.send_message(message.chat.id,"Выберите необходимую вам команду снова.")
#удаление просроченных свободных записей
def checkOfDateDelete():
    while True:
        now = time.localtime()
        now_str = str(f"{now.tm_hour}:{now.tm_min}:{now.tm_sec}")
        if str(now_str) == "23:0:0":
            conn = sqlite3.connect(r'salon_krasoti.db')
            cur = conn.cursor()
            cur.execute("delete FROM Свободные_записи WHERE дата != DATE('now') AND дата < DATE('now');")
            conn.commit()
            cur.execute("delete FROM Записи WHERE дата != DATE('now') AND дата < DATE('now');")
            conn.commit()
            cur.execute("delete FROM Записи WHERE дата = DATE('now','+1 day') and запись_подтверждена = '0';")
            conn.commit()
            cur.close()
            conn.close()

#напоминалка
def checkOfDateNap():
    checkTime = False
    while True:
        now = time.localtime()
        now_str = str(f"{now.tm_hour}:{now.tm_min}:{now.tm_sec}")
        if str(now_str) == "14:19:35":
            checkTime = True
        if checkTime == True:
            conn = sqlite3.connect(r'salon_krasoti.db')
            cur = conn.cursor()
            cur.execute('select Клиенты.telegram_id from Клиенты group by Клиенты.telegram_id;')
            klient_id = cur.fetchall()
            for i in range(len(klient_id)):
                cur.executescript(f'''
                                UPDATE Записи
                                SET запись_подтверждена = 0
                                WHERE EXISTS (
                                SELECT 1
                                FROM Клиенты
                                WHERE Клиенты.id = Записи.клиент_id
                                and Клиенты.telegram_id = '1054554990'
                                and дата = DATE('now', '+1 days')
                                );
                                ''')
                conn.commit()
                cur.execute(f'''select Клиенты.ФИО, Записи.дата, Записи.время, Услуги.название, Мастера.ФИО 
                                from Записи 
                                INNER join Клиенты on Клиенты.id = Записи.клиент_id 
                                INNER join Услуги on Записи.услуга_id = Услуги.id 
                                INNER join Мастера on Записи.мастер_id = Мастера.id 
                                where Клиенты.telegram_id = '{klient_id[i][0]}' and дата = DATE('now', '+1 days');''')
                napominanie = cur.fetchall()
                
                for j in range(len(napominanie)):
                    markup = types.InlineKeyboardMarkup()
                    button1 = types.InlineKeyboardButton(f"ПОДТВЕРДИТЬ ЗАПИСЬ", callback_data=f"+,{napominanie[j][1]},{napominanie[j][2]},{napominanie[j][4]}")
                    markup.add(button1)
                    bot.send_message(klient_id[i][0], f"Вы придёте на запись?(если да то нажмите кнопку, подтвердить запись)\nФио: {napominanie[j][0]}\nДата: {napominanie[j][1]}\nВремя: {napominanie[j][2]}\nУслуга: {napominanie[j][3]}\nМастер: {napominanie[j][4]}",parse_mode="HTML",reply_markup=markup)
                    if i == len(klient_id)-1 and j == len(napominanie)-1:
                        checkTime = False
            cur.close()
            conn.close()

if __name__ == "__main__":
    t1 = threading.Thread(target=checkOfDateDelete)
    t2 = threading.Thread(target=checkOfDateNap)
    t3 = threading.Thread(target=main_func)
    t1.start()
    t2.start()
    t3.start()

bot.polling(none_stop=True)