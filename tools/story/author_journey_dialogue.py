#!/usr/bin/env python3
"""Original contextual conversations for the single Daniel–Mara journey."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];rows=[]
def add(id,min_scene,max_scene,trigger,text):
 lines=[x.split(' | ',1) for x in text.strip().splitlines()];assert len(lines)==6 and all(len(x)==2 for x in lines)
 rows.append({'id':id,'min_scene':min_scene,'max_scene':max_scene,'trigger':trigger,'ru':[x[0] for x in lines],'en':[x[1] for x in lines]})
add('wrong_shoes',18,23,'walk','''
Мара: На правой подошве у тебя чужой след. | Mara: Your right sole has somebody else's footprint.
Дэниел: Заплатку вырезали из другой пары. | Daniel: The patch was cut from another pair.
Мара: Если нас будут искать по следам, решат, что ты ушёл сам от себя. | Mara: Anyone tracking us will think you walked away from yourself.
Дэниел: Наконец-то у меня появится убедительное алиби. | Daniel: At last I will have a convincing alibi.
Мара: Только не показывай им левый ботинок. | Mara: Just do not show them your left boot.
Дэниел: Левый я вообще берегу для официальных встреч. | Daniel: I save the left one for formal occasions anyway.
''')
add('rain_smell',18,24,'rain','''
Мара: Дождь пахнет школьной столовой. | Mara: The rain smells like the school cafeteria.
Дэниел: По-моему, это мокрый картон. | Daniel: I think that is wet cardboard.
Мара: Именно. Нам подавали его по четвергам. | Mara: Exactly. They served it to us on Thursdays.
Дэниел: А я думал, ты любила школьные обеды. | Daniel: I thought you liked school lunches.
Мара: Я любила, что за одним столом помещались все мои друзья. | Mara: I liked fitting all my friends around one table.
Дэниел: Тогда, пожалуй, дело было не в поваре. | Daniel: Then perhaps it was not about the cook.
''')
add('coffee_argument',18,24,'rest','''
Дэниел: До всего этого я варил ужасный кофе. | Daniel: Before all this, I made terrible coffee.
Мара: Почему ты рассказываешь это таким гордым голосом? | Mara: Why do you sound so proud of it?
Дэниел: Потому что на дежурстве его всё равно выпивали. | Daniel: Because everyone on duty drank it anyway.
Мара: Люди нуждались в помощи, а ты принял это за благодарность. | Mara: People needed help, and you mistook it for gratitude.
Дэниел: Это был разговор про кофе, Мара. | Daniel: This was a conversation about coffee, Mara.
Мара: Я знаю. Поэтому и улыбаюсь. | Mara: I know. That is why I am smiling.
''')
add('lost_shop',19,24,'walk','''
Дэниел: Помнишь магазин у шоссе? Мне отказывались продавать там краску. | Daniel: Remember the shop by the highway? They refused to sell me paint there.
Мара: Ты устроил чрезвычайное происшествие с кисточкой? | Mara: Did you cause an emergency involving a paintbrush?
Дэниел: Заказывал по телефону оттенки. Называл их неправильно. | Daniel: I ordered colours over the phone. I kept getting their names wrong.
Мара: Даже цвету ты пытался выдать позывной. | Mara: You tried to give even a colour a call sign.
Дэниел: Называл этот жёлтый «вечером на кухне». | Daniel: I called that yellow "an evening in the kitchen".
Мара: А вот его я бы тебе продала. | Mara: That one I would have sold you.
''')
add('night_space',18,26,'night','''
Мара: Ночью дома кажутся ближе друг к другу. | Mara: At night the houses seem closer together.
Дэниел: Не видны пустые участки между ними. | Daniel: You cannot see the empty lots between them.
Мара: Знаю. Я говорю не о расстоянии. | Mara: I know. I am not talking about distance.
Дэниел: На дежурстве я иногда оставлял свободную линию включённой. | Daniel: Sometimes on duty I left an empty line connected.
Мара: Чтобы слышать, что на другом конце кто-то дышит? | Mara: So you could hear someone breathing at the other end?
Дэниел: Иногда там был только ветер. Но и его хватало. | Daniel: Sometimes there was only wind. That was enough too.
''')
add('slow_breath',20,29,'hurt','''
Мара: Скажи что-нибудь длинное. Хочу услышать, как ты дышишь. | Mara: Say something long. I want to hear how you are breathing.
Дэниел: Я категорически возражаю против такого медицинского осмотра. | Daniel: I categorically object to this method of medical examination.
Мара: На слове «категорически» ты почти развалился. | Mara: You nearly fell apart on "categorically".
Дэниел: В следующий раз выберу слово покороче. | Daniel: Next time I will choose a shorter word.
Мара: В следующий раз скажи, что тебе больно. Бинт у тебя в рюкзаке, если не потратил. | Mara: Next time tell me it hurts. You have a bandage in your pack if you have not used it.
Дэниел: Мне больно. И я рад, что ты заметила. | Daniel: It hurts. And I am glad you noticed.
''')
add('left_hand',24,30,'walk','''
Мара: Ты открываешь все двери левой рукой. | Mara: You open every door with your left hand.
Дэниел: Правой обычно держал рацию. | Daniel: I usually held the radio in my right.
Мара: Рация теперь у меня. | Mara: I have the radio now.
Дэниел: Привычки не получают уведомлений о переводе. | Daniel: Habits do not receive transfer notices.
Мара: Тогда правой можешь подержать дверь для Рут. | Mara: Then you can hold the door for Ruth with your right.
Дэниел: С этим новым назначением я справлюсь. | Daniel: I can manage that new assignment.
''')
add('missing_recipe',25,30,'rest','''
Мара: Самое обидное — я не спросила, как мама делала тесто. | Mara: The worst part is that I never asked how Mum made her dough.
Дэниел: Наверняка записала где-нибудь на кухне. | Daniel: She probably wrote it down somewhere in the kitchen.
Мара: Она говорила «пока не почувствуешь». Это плохая единица измерения. | Mara: She said "until it feels right". That is a terrible unit of measurement.
Дэниел: Можем начать с плохого хлеба. | Daniel: We could start with bad bread.
Мара: А потом уверять всех, что именно такой и задумывался? | Mara: Then tell everyone that was how it was meant to turn out?
Дэниел: Нет. Потом попробовать ещё раз, пока мука не закончилась. | Daniel: No. Then try again, before we run out of flour.
''')
add('rain_afterward',25,30,'rain','''
Дэниел: Ты больше не считаешь шаги под дождём. | Daniel: You are not counting your steps in the rain now.
Мара: Считаю. Только не вслух. | Mara: I am counting. Just not aloud.
Дэниел: Я думал, тебе стало спокойнее. | Daniel: I thought you felt safer.
Мара: Стало. Страшно от этого быть не перестало. | Mara: I do. That does not mean I stopped being afraid.
Дэниел: Следующие сто шагов посчитаем вдвоём. | Daniel: We can count the next hundred steps together.
Мара: Ладно. Но не сбивайся на командный голос. | Mara: All right. But keep your command voice out of it.
''')
add('future_window',27,30,'walk','''
Мара: Если останусь в саду, переставлю стол к другому окну. | Mara: If I stay at the orchard, I will move the table to the other window.
Дэниел: Там меньше света. | Daniel: There is less light there.
Мара: Зато видно, кто идёт по дороге. И не нужно вставать каждую минуту. | Mara: But you can see who is coming up the road. You do not have to stand up every minute.
Дэниел: Я могу помочь его перенести. | Daniel: I could help you move it.
Мара: Я не просила тебя поселиться там. | Mara: I did not ask you to move in.
Дэниел: Я говорил только про стол. Он выглядит очень упрямым. | Daniel: I only meant the table. It looks very stubborn.
''')
add('ordinary_names',26,30,'night','''
Мара: Когда всё закончится, я хочу услышать по радио прогноз погоды. | Mara: When this is over, I want to hear a weather forecast on the radio.
Дэниел: Я могу передать его хоть сейчас. | Daniel: I could broadcast one right now.
Мара: Нет. Хочу злиться, что опять обещали солнце и ошиблись. | Mara: No. I want to be annoyed because they promised sunshine and got it wrong again.
Дэниел: А потом позвонить в диспетчерскую и пожаловаться? | Daniel: Then call the dispatch office and complain?
Мара: Лично прийти. Чтобы тебя было труднее выключить. | Mara: Come in person. So you would be harder to switch off.
Дэниел: Тогда я оставлю для тебя свободный стул. | Daniel: Then I will keep a chair free for you.
''')
add('shared_silence',28,30,'water','''
Дэниел: Ты давно ничего не говоришь. | Daniel: You have not said anything for a while.
Мара: Я смотрю, как вода обходит камень. | Mara: I am watching the water go around that stone.
Дэниел: И о чём это тебе напоминает? | Daniel: What does it remind you of?
Мара: Ни о чём. Иногда вода просто обходит камень. | Mara: Nothing. Sometimes water just goes around a stone.
Дэниел: Можно я тоже посмотрю? | Daniel: May I watch it too?
Мара: Конечно. Посиди рядом со мной. Давай просто немного помолчим. | Mara: Of course. Sit beside me. Let us just be quiet for a while.
''')
d={'schema':1,'purpose':'Contextual relationship scenes within the continuous main journey; not separate quests.','conversations':rows,'recorded_voice_complete':False,'measured_gameplay_hours':None}
(ROOT/'BuildData/story/journey-dialogue.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print('JOURNEY_DIALOGUE_AUTHORED',len(rows),sum(len(r['ru']) for r in rows))
