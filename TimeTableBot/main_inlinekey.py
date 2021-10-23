# import telebot
# from keep_alive import keep_alive
# from telebot import custom_filters

# bot = telebot.TeleBot("2037363678:AAF10C7_2MM_ue7ycRCIbs2K6ry1MeEu3_8")



# @bot.message_handler(commands=['start'])
# def start_ex(message):
#     """
#     Start command. Here we are starting state
#     """
#     bot.set_state(message.chat.id, 1)
#     bot.send_message(message.chat.id, 'Hi, write me a name')
 

 
# @bot.message_handler(state="*", commands='cancel')
# def any_state(message):
#     """
#     Cancel state
#     """
#     bot.send_message(message.chat.id, "Your state was cancelled.")
#     bot.delete_state(message.chat.id)

# @bot.message_handler(state=1)
# def name_get(message):
#     """
#     State 1. Will process when user's state is 1.
#     """
#     bot.send_message(message.chat.id, f'Now write me a surname')
#     bot.set_state(message.chat.id, 2)
#     with bot.retrieve_data(message.chat.id) as data:
#         data['name'] = message.text
 
 
# @bot.message_handler(state=2)
# def ask_age(message):
#     """
#     State 2. Will process when user's state is 2.
#     """
#     bot.send_message(message.chat.id, "What is your age?")
#     bot.set_state(message.chat.id, 3)
#     with bot.retrieve_data(message.chat.id) as data:
#         data['surname'] = message.text
 
# # result
# @bot.message_handler(state=3, is_digit=True)
# def ready_for_answer(message):
#     with bot.retrieve_data(message.chat.id) as data:
#         bot.send_message(message.chat.id, "Ready, take a look:\n<b>Name: {name}\nSurname: {surname}\nAge: {age}</b>".format(name=data['name'], surname=data['surname'], age=message.text), parse_mode="html")
#     bot.delete_state(message.chat.id)

# #incorrect number
# @bot.message_handler(state=3, is_digit=False)
# def age_incorrect(message):
#     bot.send_message(message.chat.id, 'Looks like you are submitting a string in the field age. Please enter a number')

# # register filters

# bot.add_custom_filter(custom_filters.StateFilter(bot))
# bot.add_custom_filter(custom_filters.IsDigitFilter())

# # set saving states into file.
# #bot.enable_saving_states() # you can delete this if you do not need to save states
# keep_alive()

# bot.infinity_polling()

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


bot = telebot.TeleBot("2037363678:AAF10C7_2MM_ue7ycRCIbs2K6ry1MeEu3_8")

def gen_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Yes", callback_data="/send"),
                               InlineKeyboardButton("No", callback_data="/send"))
    return markup

# @bot.callback_query_handler(func=lambda call: True)
# def callback_query(call):
#     if call.data == "cb_yes":
#         bot.answer_callback_query(call.id, "Answer is Yes")
#     elif call.data == "cb_no":
#         bot.answer_callback_query(call.id, "Answer is No")

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    bot.send_message(message.chat.id, "Yes/no?", reply_markup=gen_markup(), )

@bot.message_handler(commands = ["send"])
def send_func(message):
    bot.send_message(message.chat.id, "smth")

bot.infinity_polling()