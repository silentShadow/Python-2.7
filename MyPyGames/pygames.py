"""
This will be a game spun off the PyWars created by Mark Baggett of SANS
"""
import time
from random import randint


TIME_THEN = []

# these need to be private and not viewable by the players
#
bank_of_qs = {0:"Return the string returned to you by data()",
              1:"Determine the length of this question",
              2:"This is question 3",
              3:"This is question 4",
              4:"This is question 5",
              5:"This is question 6",
              6:"This is question 7",
              7:"This is question 8",
              8:"This is question 9"}


# these need to be private and not viewable by the players
#
bank_of_answers = {0:{"This is the answer!":1},
                   1:{len(bank_of_qs[1]):1},
                   2:{"This is question 3":2}}


def answer(qstn, answr):
    """pass"""
    if qstn in bank_of_answers.keys():
        #print(TIME_THEN)
        #print("then: {}, now: {}, diff: {}".format(int(TIME_THEN[-1]), int(time.time()), int(TIME_THEN[-1] - time.time())))
        if answr == bank_of_answers[qstn].keys()[-1]:
            if int(TIME_THEN[-1] - time.time()) >= 0:
                # need to submit points to a scoring server
                print("Congrats, you have been awarded {} point(s)".format(bank_of_answers[qstn].values()[-1]))
            else:
                print("You took too much time to answer, try again")
        else:
            print("That is not the correct answer")


    if qstn not in bank_of_answers.keys():
        print("Hey, that is not a valid question to answer")




def question(num):
    """
    this will be the question bank that will present the user with the
    questions they will need to answer correctly to receive points

    the harder the question for more points it will be worth
    """

    # make sure user is going for the right question
    if num in bank_of_qs.keys():
        return bank_of_qs[num]

    if num not in bank_of_qs.keys():
        return "Hey, that is not a valid question to choose"



def data(num):
    """This is the string for question 1"""
    TIME_THEN.append(time.time())
    #print(TIME_THEN[-1])

    return bank_of_answers[num].keys()[-1]
