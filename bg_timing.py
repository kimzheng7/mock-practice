import time
import pyttsx3
import threading

speech = pyttsx3.init()
def instantly_say(text, wait_time):
    speech.say(text)
    threading.Thread(target=speech.runAndWait).start()
    time.sleep(wait_time)

# pre game
instantly_say("Game begins in 1 minute. \\
    Organise columns in agressor direction, fill size, price, passive trader, aggressive trader.",
    45)
instantly_say("Game begins in 15 seconds. Prepare CB quotes.", 10)
instantly_say("Post CB quotes in 5.", 1)
instantly_say("4", 1)
instantly_say("3", 1)
instantly_say("2", 1)
instantly_say("1", 1)
instantly_say("", 105)

# pre spring
instantly_say("JTR comes in 15 seconds. Prepare quotes.", 10)
instantly_say("Post JTR quotes in 5.", 1)
instantly_say("4", 1)
instantly_say("3", 1)
instantly_say("2", 1)
instantly_say("1", 1)

# post spring
instantly_say("Record individual harvest and MM CB.", 25)
instantly_say("TB comes in 15 seconds. Prepare quote pulling.", 10)
instantly_say("Pull TB quotes in 5.", 1)
instantly_say("4", 1)
instantly_say("3", 1)
instantly_say("2", 1)
instantly_say("1", 1)
instantly_say("MM around fair, and prepare PB quote.", 65)
instantly_say("Census is coming. ")
