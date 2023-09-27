import telebot
from telebot import types
import sqlite3
from langdetect import detect
from random import choice


bot = telebot.TeleBot("...")


# "START" command sends an introductory message
@bot.message_handler(commands=["start"])
def start(message):
    # Connect to the database and create a table 
    conn = sqlite3.connect("words.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS words (id INTEGER PRIMARY KEY AUTOINCREMENT, korean TEXT, english TEXT)")
    conn.commit()
    cur.close()
    conn.close()

    # Menu buttons
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("Add a new word", callback_data="new_word")
    btn2 = types.InlineKeyboardButton("Test your knowledge", callback_data="test_know")
    btn3 = types.InlineKeyboardButton("Show all words", callback_data="show_words")
    btn4 = types.InlineKeyboardButton("Translation of the word", callback_data="dictionary")
    markup.add(btn1, btn3, btn4, btn2)
    bot.send_message(message.chat.id, "<b>🇰🇷 Hello! This is the place for learning Korean 🇰🇷</b>\n\n" \
                         "🔹 To add a Korean word and its English translation to the database, tap the button <b>'Add a new word'</b>.\n" \
                         "🔹 To see all pairs of words in the database, tap the button <b>'Show all words'</b>.\n" \
                         "🔹 To find the English translation/meaning of Korean word or vice versa, tap the button <b>'Translation of the word'</b>.\n" \
                         "🔹 To test your knowledge of Korean, tap the button <b>'Test you knowledge'</b>.\n\n" \
                            "👇🏻 Choose what you want to do 👇🏻", reply_markup=markup, parse_mode="html")


# "STOP" command stops running the bot
@bot.message_handler(commands=['stop'])
def stop(message):
    bot.stop_bot()


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    # When the button "Back" is pressed
    if call.data == "menu":
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("Add a new word", callback_data="new_word")
        btn2 = types.InlineKeyboardButton("Test your knowledge", callback_data="test_know")
        btn3 = types.InlineKeyboardButton("Show all words", callback_data="show_words")
        btn4 = types.InlineKeyboardButton("Translation of the word", callback_data="dictionary")
        markup.add(btn1, btn3, btn4, btn2)
        bot.send_message(call.message.chat.id, "<b>🇰🇷 Hello! This is the place for learning Korean 🇰🇷</b>\n\n" \
                         "🔹 To add a Korean word and its English translation to the database, tap the button <b>'Add a new word'</b>.\n" \
                         "🔹 To see all pairs of words in the database, tap the button <b>'Show all words'</b>.\n" \
                         "🔹 To find the English translation/meaning of Korean word or vice versa, tap the button <b>'Translation of the word'</b>.\n" \
                         "🔹 To test your knowledge of Korean, tap the button <b>'Test you knowledge'</b>.\n\n" \
                            "👇🏻 Choose what you want to do 👇🏻", reply_markup=markup, parse_mode="html")
    
    # When the button "Add a new word" is pressed
    elif call.data == "new_word":
        bot.send_message(call.message.chat.id, "Send a Korean word and its English translation with a dash between them, as shown in the example (eg. '가다 - to go') ✏️")
        bot.register_next_step_handler(call.message, add_pair)

    # When the button "Test your knowledge" is pressed
    elif call.data == "test_know":
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("English", callback_data="kor_test")
        btn2 = types.InlineKeyboardButton("Korean", callback_data="eng_test")
        markup.add(btn1, btn2)
        bot.send_message(call.message.chat.id, "▫️ To guess an English word by its Korean translation, tap the button <b>'English'</b> 🇺🇸\n" \
                         "▫️ To guess a Korean word by its English translaion, tap the button <b>'Korean'</b> 🇰🇷", reply_markup=markup, parse_mode="html")
    
    # When the button "Show all words" is pressed
    elif call.data == "show_words":
        conn = sqlite3.connect("test.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM words")

        words = cur.fetchall()

        info = ""
        for el in words:
            info += f"{el[1]} - {el[2]}\n"

        cur.close()
        conn.close()

        bot.send_message(call.message.chat.id, f"🖇<u>The list of words</u>🖇\n{info}", parse_mode="html")

        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("Back", callback_data="menu")
        markup.add(btn1)
        bot.send_message(call.message.chat.id, "▫️ To go back to menu, tap the button <b>'Back'</b>", reply_markup=markup, parse_mode="html")
    
    # When the button "Translation of the word" is pressed
    elif call.data == "dictionary":
        bot.send_message(call.message.chat.id, "Send <u>a word (English or Korean)</u> to see its translation and meaning in the dictionary 📖", parse_mode="html")
        bot.register_next_step_handler(call.message, find_in_dic)

    # When one chooses to test their korean knowledge by pressing the button "Korean"
    elif call.data == "eng_test":
        bot.send_message(call.message.chat.id, "Send <b>'begin'</b> to start a test 🚩", parse_mode="html")
        bot.register_next_step_handler(call.message, test_eng)
    
    # When one chooses to test their korean knowledge by pressing the button "English"
    elif call.data == "kor_test":
        bot.send_message(call.message.chat.id, "Send <b>'begin'</b> to start a test 🚩", parse_mode="html")
        bot.register_next_step_handler(call.message, test_kor)


# Add a pair of words to the database
def add_pair(message):
    try:
        kor, eng = message.text.lower().split("-")
        kor = kor.strip()
        eng = eng.strip()

        if detect(kor) == "ko" and eng.isascii():
            conn = sqlite3.connect("test.db")
            cur = conn.cursor()

            cur.execute("SELECT * FROM words where korean = ?", (kor, ))

            exist = cur.fetchone()

            # If the word is new
            if exist is None:
                cur.execute("INSERT INTO words (korean,english) VALUES(?,?)", (kor, eng,))
                conn.commit()

                markup = types.InlineKeyboardMarkup(row_width=2)
                btn1 = types.InlineKeyboardButton("Back", callback_data="menu")
                btn2 = types.InlineKeyboardButton("Add", callback_data="new_word")
                markup.add(btn2, btn1)

                bot.send_message(message.chat.id, "✨ <u>The word is successfully added to the database!</u> ✨\n" \
                                 "▫️ To add another word, tap the button <b>'Add'</b>\n" \
                                    "▫️ To go back to menu, tap the button <b>'Back'</b>", reply_markup=markup, parse_mode="html")
            
            # If the word is already in the table
            else:
                markup = types.InlineKeyboardMarkup(row_width=2)
                btn1 = types.InlineKeyboardButton("Back", callback_data="menu")
                btn2 = types.InlineKeyboardButton("Add", callback_data="new_word")
                markup.add(btn2, btn1)

                bot.send_message(message.chat.id, "❗️ <u>The word is already in the database!</u> ❗️\n"\
                                 "▫️ To add another word, tap the button <b>'Add'</b>\n" \
                                    "▫️ To go back to menu, tap the button <b>'Back'</b>", reply_markup=markup, parse_mode="html")

            cur.close()
            conn.close()
        
        # The wrong language is used
        else:
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn1 = types.InlineKeyboardButton("Back", callback_data="menu")
            btn2 = types.InlineKeyboardButton("Again", callback_data="new_word")
            markup.add(btn2, btn1)
            bot.send_message(message.chat.id, "❗️ <u>You use the wrong language!</u> ❗️\n"\
                                 "▫️ To try again, tap the button <b>'Again'</b>\n" \
                                    "▫️ To go back to menu, tap the button <b>'Back'</b>", reply_markup=markup, parse_mode="html")
    
    # The format of data is wrong
    except:
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("Back", callback_data="menu")
        btn2 = types.InlineKeyboardButton("Again", callback_data="new_word")
        markup.add(btn2, btn1)
        bot.send_message(message.chat.id, "❗️ <u>Invalid input!</u> ❗️\n"\
                                 "▫️ To try again, tap the button <b>'Again'</b>\n" \
                                    "▫️ To go back to menu, tap the button <b>'Back'</b>", reply_markup=markup, parse_mode="html")
        

# Select a random pair of words from the table and send its english part
def test_eng(message):
    if message.text == "begin" or message.text == "next":
        conn = sqlite3.connect("test.db")
        cur = conn.cursor()

        cur.execute("SELECT * FROM words")

        words = cur.fetchall()

        pair = choice(words)
        eng_word = pair[2]
        kor_word = pair[1]

        cur.close()
        conn.close()

        bot.send_message(message.chat.id, eng_word)
        bot.register_next_step_handler(message, check_eng_word, kor_word)
    elif message.text == "stoptest":
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("Back", callback_data="menu")
        markup.add(btn1)

        bot.send_message(message.chat.id, "The test is stopped! 🛑\n" \
                            "To go back to menu, tap the button <b>'Back'</b>", reply_markup=markup, parse_mode="html")
    else:
        bot.send_message(message.chat.id, "❗️ <u>Invalid input!</u> ❗️\n" \
                         "▫️ To start a test, send <b>'begin'</b>\n" \
                            "▫️ To continue the test, send <b>'next'</b>\n" \
                                "▫️ To stop the test, send <b>'stoptest'</b>", parse_mode="html")
        bot.register_next_step_handler(message, test_eng)

# Select a random pair of words from the table and send its korean part
def test_kor(message):
    if message.text == "begin" or message.text == "next":
        conn = sqlite3.connect("test.db")
        cur = conn.cursor()

        cur.execute("SELECT * FROM words")

        words = cur.fetchall()

        pair = choice(words)
        kor_word = pair[1]
        eng_word = pair[2]

        cur.close()
        conn.close()

        bot.send_message(message.chat.id, kor_word)
        bot.register_next_step_handler(message, check_kor_word, eng_word)
    elif message.text == "stoptest":
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("Back", callback_data="menu")
        markup.add(btn1)

        bot.send_message(message.chat.id, "The test is stopped! 🛑\n" \
                         "To go back to menu, tap the button <b>'Back'</b>", reply_markup=markup, parse_mode="html")
    else:
        bot.send_message(message.chat.id, "❗️ <u>Invalid input!</u> ❗️\n" \
                         "▫️ To start a test, send <b>'begin'</b>\n" \
                            "▫️ To continue the test, send <b>'next'</b>\n" \
                                "▫️ To stop the test, send <b>'stoptest'</b>", parse_mode="html")
        bot.register_next_step_handler(message, test_kor)

# Check if one sends the right translation of the english word
def check_eng_word(message, kor_word):
    if message.text.lower().strip() == kor_word:
        bot.send_message(message.chat.id, "You are right! ✅\n" \
                         "▫️ To continue the test, send <b>'next'</b>\n" \
                            "▫️ To stop the test, send <b>'stoptest'</b>", parse_mode="html")
        bot.register_next_step_handler(message, test_eng)
    elif message.text.lower().strip() == "stoptest":
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("Back", callback_data="menu")
        markup.add(btn1)

        bot.send_message(message.chat.id, "The test is stopped! 🛑\n" \
                         "To go back to menu, tap the button <b>'Back'</b>", reply_markup=markup, parse_mode="html")
    else:
        bot.send_message(message.chat.id, "You are wrong! ❌\n" \
                         "▫️ To try again, send a new answer\n" \
                            "▫️ To stop the test, send <b>'stoptest'</b>", parse_mode="html")
        bot.register_next_step_handler(message, check_eng_word, kor_word)

# Check if one sends the right translation of the korean word
def check_kor_word(message, eng_word):
    if message.text.lower().strip() == eng_word:
        bot.send_message(message.chat.id, "You are right! ✅\n" \
                         "▫️ To continue the test, send <b>'next'</b>\n" \
                            "▫️ To stop the test, send <b>'stoptest'</b>", parse_mode="html")
        bot.register_next_step_handler(message, test_kor)
    elif message.text.lower().strip() == "stoptest":
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("Back", callback_data="menu")
        markup.add(btn1)

        bot.send_message(message.chat.id, "The test is stopped! 🛑\n" \
                         "To go back to menu, tap the button <b>'Back'</b>", reply_markup=markup, parse_mode="html")
    else:
        bot.send_message(message.chat.id, "You are wrong! ❌\n" \
                         "▫️ To try again, send a new answer\n" \
                            "▫️ To stop the test, send <b>'stoptest'</b>", parse_mode="html")
        bot.register_next_step_handler(message, check_kor_word, eng_word)

# Open a dictionary 
def find_in_dic(message):
    word = message.text.lower().strip()
    url = f"https://korean.dict.naver.com/koendict/#/search?range=all&query={word}"
    bot.send_message(message.chat.id, f"<u>Click the following link:</u>\n{url}", parse_mode="html")
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("Back", callback_data="menu")
    btn2 = types.InlineKeyboardButton("Again", callback_data="dictionary")
    markup.add(btn2, btn1)
    bot.send_message(message.chat.id, "▫️ To search another word, tap the button <b>'Again'</b>\n" \
                     "▫️ To go back to menu, tap the button <b>'Back'</b>", reply_markup=markup, parse_mode="html")


def main():
	try:
		bot.polling(none_stop=True)
	except Exception as er:
		print(f"Error: {er}")


if __name__ == '__main__':
	main()