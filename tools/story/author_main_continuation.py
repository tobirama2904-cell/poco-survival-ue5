#!/usr/bin/env python3
"""One continuous return journey, not six mandatory county side quests."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/scene'))
from county_layout import height,bridge_deck
p=ROOT/'BuildData/story/low-water.json';d=json.loads(p.read_text());d['scenes']=d['scenes'][:18]
goals=[('Найти радио у депо.','Find the depot radio.'),('Забрать снаряжение у лестницы и поговорить с Марой.','Collect the equipment beside the stairs and speak with Mara.'),('Добраться до школы: там сохранился журнал эвакуации.','Reach the school and its evacuation log.'),('Найти Рут в клинике.','Find Ruth at the clinic.'),('Проверить старую отметку воды.','Check the old water mark.'),('Поговорить с Оуэном у переправы.','Speak to Owen at the crossing.'),('Найти привод у мельницы.','Find the mill actuator.'),('Прослушать запись диспетчерской.','Listen to the dispatch recording.'),('Осмотреть квартиру над нижним кварталом.','Inspect the apartment above the lower quarter.'),('Подняться к передающей башне.','Reach the transmission tower.'),('Проверить убежище у переправы.','Check the shelter by the crossing.'),('Вернуться к общему каналу.','Return to the public channel.'),('Вернуться к мельнице вместе с Марой.','Return to the mill with Mara.'),('Поговорить у шлюза, прежде чем трогать рычаги.','Speak at the gate before touching the levers.'),('Открыть канал или удержать затвор.','Open the channel or hold the gate.'),('Вернуться к радио в депо.','Return to the depot radio.'),('Встретиться с Марой у школы.','Meet Mara at the school.'),('Остаться на связи с клиникой.','Stay in contact with the clinic.')]
for s,(ru,en) in zip(d['scenes'],goals):s['intent_ru']=ru;s['intent_en']=en;s['required_events']=0;s['escort']=0;s['focus']='';s['part']=1
# Preserve the original voiced lines and IDs; only the unvoiced end-of-part text changes.
d['scenes'][17]['title']='Часть I • Ответный вызов';d['scenes'][17]['ru'][-1]='Беллуэзер открыт для исследования. История продолжается. Оставайтесь на связи с клиникой.';d['scenes'][17]['en'][-1]='Bellwether remains open to explore. The story continues. Stay in contact with the clinic.'
def scene(id,title,xy,cinematic,mask,escort,focus,goal,en_goal,lines):
 pairs=[x.split(' | ',1) for x in lines.strip().splitlines()];assert len(pairs)==8 and all(len(x)==2 for x in pairs)
 x,y=xy;z=bridge_deck()[2]+.15 if id in ('bridge_latch','other_bank') else height(x,y) if max(abs(x),abs(y))>345 else 0
 d['scenes'].append({'id':id,'title':'Часть II • '+title,'position':[x,y,z],'cinematic':cinematic,'gate':0,'required_events':mask,'escort':escort,'focus':focus,'intent_ru':goal,'intent_en':en_goal,'part':2,'ru':[x[0] for x in pairs],'en':[x[1] for x in pairs]})
scene('return_call','Тот, кто ответил',(10,40),True,0,1,'Mara','Пойти с Марой к дороге на станцию смотрителя.','Follow the ranger-station road with Mara.','''
Рут: Дэниел, не выключай радио. Я не закончила. | Ruth: Daniel, keep the radio on. I have not finished.
Дэниел: Ты сказала, что течение успокоилось. | Daniel: You said the current had settled.
Рут: Вода — да. В клинике просела лестница. На верхнем этаже остались люди. | Ruth: The water has. The clinic stairs have subsided. People are still upstairs.
Мара: Сколько ты можешь вывести сама? | Mara: How many can you bring out yourself?
Рут: Я спрашиваю их, кто может идти. Не ставлю цифру в отчёт. | Ruth: I am asking who can walk. Not putting a number in a report.
Дэниел: Где ближайший исправный приёмник? Я проверю дорогу для вас. | Daniel: Where is the nearest working receiver? I will check a route for you.
Мара: На станции смотрителя. Пойдём вместе. По радио ты слишком легко звучишь уверенно. | Mara: At the ranger station. We go together. You sound certain far too easily on the radio.
Дэниел: Тогда скажешь мне это в лицо. Я буду рядом. | Daniel: Then you can tell me to my face. I will be there.
''')
scene('walking_company','Рядом, а не впереди',(0,14),False,0,1,'','Дойти до станции смотрителя и восстановить приёмник. Нужны дерево и деталь.','Reach the ranger station and repair its receiver. Bring wood and scrap.','''
Мара: Ты всё время прибавляешь шаг. | Mara: You keep walking faster.
Дэниел: Привычка. Если быстро прийти, кажется, что ещё можно успеть. | Daniel: Habit. Getting there quickly makes it feel as though there is still time.
Мара: А тот, кто не успевает за тобой? | Mara: And the person who cannot keep up?
Дэниел: Раньше я считал, что он сам скажет. | Daniel: I used to think they would tell me.
Мара: Моя мать никогда не говорила. Даже когда обувь наполнялась кровью. | Mara: My mother never did. Not even when her shoes filled with blood.
Дэниел: Я могу идти медленнее. | Daniel: I can slow down.
Мара: Не обещай. Просто иди. | Mara: Do not promise it. Just walk.
Дэниел: Хорошо. | Daniel: All right.
''')
scene('receiver_restored','Голос без помех',(675,-460),True,1,1,'Mara','Выслушать Рут и проверить маршрут к саду Эллисов.','Listen to Ruth and check the route to Ellis Orchard.','''
Дэниел: Контакт закреплён. Рут, слышишь нас? | Daniel: The contact is secured. Ruth, can you hear us?
Рут: Теперь слышу, как ты дышишь. Не наваливайся на микрофон. | Ruth: I can hear you breathing now. Do not lean on the microphone.
Мара: Значит, до свадьбы доживёшь. Ругаешься как обычно. | Mara: You will outlive us yet. You sound as cross as ever.
Рут: Только не устраивайте свадьбу в моей палате. Я там только убралась. | Ruth: Just do not hold a wedding in my ward. I have only just cleaned it.
Дэниел: Кто идёт с тобой? | Daniel: Who is coming with you?
Рут: Ходячих встретят у нижнего входа. Я выйду последней. Нога плохо держит. | Ruth: The people who can walk will be met at the lower entrance. I am coming out last. My leg is giving way.
Мара: Ты собиралась сообщить нам об этом когда-нибудь? | Mara: Were you planning to tell us that at some point?
Рут: Как только нашла бы время перестать быть врачом. | Ruth: As soon as I found time to stop being the doctor.
''')
scene('not_a_number','Последняя в списке',(675,-450),False,1,1,'','Найти перевязочный запас в саду Эллисов.','Find the dressing reserve at Ellis Orchard.','''
Мара: Она не попросит помочь, пока в здании остаётся хоть кто-нибудь. | Mara: She will not ask for help while anyone is left in that building.
Дэниел: Тогда не будем ждать просьбы. | Daniel: Then we do not wait for her to ask.
Мара: А решение за неё тоже примем? | Mara: Shall we make her decision for her too?
Дэниел: Принесём то, что позволит ей выйти. Остальное она решит сама. | Daniel: We bring what will let her leave. She decides the rest.
Мара: В нашем саду осталась аптечка. Погреб выше уровня воды. | Mara: There is a first-aid reserve in our orchard. The cellar is above the water.
Дэниел: Это сад твоей семьи? | Daniel: Your family’s orchard?
Мара: Я ещё не научилась говорить «бывшем». | Mara: I have not learned to call it our former orchard yet.
Дэниел: И не обязана. | Daniel: You do not have to.
''')
scene('orchard_dressing','То, что оставили другим',(780,590),False,3,1,'','Вернуться к Рут с перевязкой.','Return to Ruth with the dressing.','''
Мара: Нашлась. Мама заворачивала всё в ткань, даже пустые банки. | Mara: Found it. Mum wrapped everything in cloth, even empty jars.
Дэниел: Почему? | Daniel: Why?
Мара: Чтобы стекло не стучало, когда младшие спят. | Mara: So the glass would not rattle while the little ones slept.
Дэниел: Теперь это пригодится нам. | Daniel: It will help us now.
Мара: Только не говори, что всё было не зря. | Mara: Just do not tell me it was all worth something.
Дэниел: Я собирался сказать: спасибо, что привела. | Daniel: I was going to say thank you for bringing me here.
Мара: Тогда спасибо принято. Больше пока ничего. | Mara: Then the thanks are accepted. Nothing more for now.
Дэниел: Мне достаточно. | Daniel: That is enough for me.
''')
scene('unwritten_letter','Письмо без адреса',(760,580),False,3,1,'','Дойти до клиники с отдельным медицинским комплектом для Рут.','Reach the clinic with Ruth’s protected medical pack.','''
Дэниел: Я писал тебе после эвакуации. | Daniel: I wrote to you after the evacuation.
Мара: Я не получала писем. | Mara: I received no letters.
Дэниел: Я не отправил. Каждый раз начинал с объяснения, почему ничего нельзя было изменить. | Daniel: I never sent them. Every time I began by explaining why nothing could have been changed.
Мара: Удобно. Можно отвечать и не услышать ответа. | Mara: Convenient. You can answer without hearing a reply.
Дэниел: Да. | Daniel: Yes.
Мара: А потом? | Mara: And then?
Дэниел: Потом заканчивалась бумага. Не оправдания. | Daniel: Then I ran out of paper. Not excuses.
Мара: Оставь письма при себе. Сейчас нам нужна перевязка. | Mara: Keep the letters. What we need now is the dressing.
''')
scene('clinic_step','Одна ступень',( -188,43),True,7,1,'Ruth','Вывести Рут к выходу из клиники.','Bring Ruth to the clinic exit.','''
Рут: Осторожнее. Это моя единственная приличная штанина. | Ruth: Careful. That is my only decent trouser leg.
Мара: Считаешь это приличным? | Mara: You call this decent?
Рут: Здесь никто не выдавал мне форму за красивые глаза. | Ruth: Nobody here ever gave me a uniform for my pretty eyes.
Дэниел: Повязка держит. Можешь встать? | Daniel: The dressing holds. Can you stand?
Рут: Могу попробовать. Не дёргай меня, если я остановлюсь. | Ruth: I can try. Do not pull me along if I stop.
Мара: Мы подождём. | Mara: We will wait.
Рут: Вы оба умеете это произносить. Посмотрим, умеете ли делать. | Ruth: You both know how to say that. We will see whether you can do it.
Дэниел: Начнём с одной ступени. | Daniel: We start with one step.
''')
scene('outside_again','Небо без потолка',(-180,38),False,7,2,'','Довести Рут до моста через реку. Не оставлять её позади.','Escort Ruth to the river bridge. Do not leave her behind.','''
Рут: Снаружи всегда было так шумно? | Ruth: Was it always this noisy outside?
Мара: Ты слишком долго слышала только наш коридор. | Mara: You have spent too long hearing nothing but our corridor.
Рут: Я думала, что однажды выйду и начну плакать. | Ruth: I thought I would start crying when I finally stepped outside.
Дэниел: А сейчас? | Daniel: And now?
Рут: Сейчас мне хочется поправить чужую вывеску. Она висит криво. | Ruth: Now I want to straighten that sign. It is crooked.
Мара: Значит, с тобой всё в порядке. | Mara: Then you are all right.
Рут: Нет. Просто я всё ещё я. | Ruth: No. I am simply still myself.
Дэниел: Вывеска подождёт. Мы тоже, если понадобится. | Daniel: The sign can wait. So can we, if we need to.
''')
scene('bridge_latch','Не закрывать за собой',(430,40),False,15,2,'','Перевести Рут через мост к восточному берегу.','Bring Ruth across the bridge to the east bank.','''
Мара: Фиксатор снят. Проход свободен. | Mara: The latch is released. The way is clear.
Оуэн: После себя закройте. Ночью сюда придут чужие. | Owen: Close it behind you. Strangers will come here at night.
Дэниел: Сегодня мы тоже пришли с другого берега. | Daniel: Today we came from the other bank too.
Оуэн: Я не о вас. | Owen: I do not mean you.
Мара: Обычно так и начинают. | Mara: That is usually how it begins.
Рут: Мне нужен свободный проход, а не спор на середине моста. | Ruth: What I need is a clear crossing, not an argument halfway across the bridge.
Дэниел: Проход останется свободным. Я отвечу за это, когда вернусь. | Daniel: The crossing stays clear. I will answer for it when I return.
Оуэн: Тогда возвращайся. Не присылай вместо себя объяснение. | Owen: Then return. Do not send an explanation in your place.
''')
scene('other_bank','Другой берег',(555,40),False,15,2,'','Продолжать путь к саду вместе с Рут.','Continue to the orchard with Ruth.','''
Рут: Не смотри всё время на мою ногу. Я чувствую каждый взгляд. | Ruth: Stop watching my leg. I can feel every glance.
Дэниел: Скажи, если нужно остановиться. | Daniel: Tell me if you need to stop.
Мара: Дэниел, ты опять торопишься. | Mara: Daniel, you are rushing again.
Дэниел: Да. Помню. Остановимся здесь. | Daniel: Yes. I remember. We stop here.
Рут: Вы что-то обсуждали без меня? | Ruth: Have you two been discussing something without me?
Мара: Учились ходить. | Mara: Learning to walk.
Рут: Отлично. Я почти шестьдесят лет занимаюсь тем же. | Ruth: Excellent. I have been working on that for nearly sixty years.
Дэниел: Тогда у нас хороший учитель. | Daniel: Then we have a good teacher.
''')
scene('the_way_back','Дорога назад',(700,480),False,15,2,'','Довести Рут до сада и включить свет у убежища.','Bring Ruth to the orchard and switch on the shelter light.','''
Мара: Ты ведь понимаешь, что дорога назад ничего не отменит? | Mara: You know the journey back will not undo anything, do you?
Дэниел: Да. | Daniel: Yes.
Мара: Я могу дойти с тобой до самого сада и всё равно злиться. | Mara: I can walk all the way to the orchard with you and still be angry.
Дэниел: Ты не обязана выбирать что-то одно. | Daniel: You do not have to choose between the two.
Рут: А я могу любить вас обоих и хотеть, чтобы вы наконец помолчали. | Ruth: And I can love you both and wish you would finally be quiet.
Мара: Любить нас обоих — плохое медицинское решение. | Mara: Loving us both is a poor medical decision.
Рут: Я сегодня не на смене. | Ruth: I am off duty today.
Дэниел: Тогда остаток пути — без приказов. | Daniel: Then no orders for the rest of the way.
''')
scene('a_place_to_return','Куда возвращаются',(780,590),True,31,2,'Ruth','Исследовать Беллуэзер; убежище в саду остаётся доступным.','Explore Bellwether; the orchard shelter remains available.','''
Рут: Свет включили для меня или чтобы видеть, как я ворчу? | Ruth: Is the light for me, or so you can see me complain?
Мара: Для того, кто придёт следующим. | Mara: For whoever comes next.
Дэниел: На двери нет списка. | Daniel: There is no list on the door.
Рут: Тогда поставьте стул. Людям должно быть куда сесть, прежде чем отвечать на вопросы. | Ruth: Put a chair there, then. People need somewhere to sit before answering questions.
Мара: Я останусь, пока она не уснёт. | Mara: I will stay until she falls asleep.
Дэниел: А потом? | Daniel: And afterwards?
Мара: Потом найдём Оуэна. Вместе. Это ещё не прощение, если ты об этом. | Mara: Afterwards we find Owen. Together. It is still not forgiveness, if that is what you are wondering.
Дэниел: Я хотел спросить, оставить ли тебе место у двери. | Daniel: I was going to ask whether to leave you a place beside the door.
''')
# Intent describes what is needed to ENTER the current scene, not its next step.
entry_goals={
 'return_call':('Ответить на вызов Рут вместе с Марой.','Answer Ruth’s call with Mara.'),
 'receiver_restored':('На станции смотрителя восстановить приёмник: дерево и деталь.','Repair the ranger-station receiver with wood and scrap.'),
 'not_a_number':('Поговорить с Марой у северного выхода со станции.','Speak with Mara at the north side of the station.'),
 'orchard_dressing':('В саду Эллисов забрать отдельный медицинский комплект для Рут.','Collect Ruth’s protected medical pack at Ellis Orchard.'),
 'clinic_step':('В клинике помочь Рут, используя медицинский комплект.','Use the medical pack to help Ruth at the clinic.'),
 'outside_again':('Дождаться Рут у выхода из клиники.','Wait for Ruth outside the clinic.'),
 'bridge_latch':('У западной части моста снять фиксатор и дождаться Рут.','Release the latch on the western bridge deck and wait for Ruth.'),
 'a_place_to_return':('Привести Рут в сад и включить свет у убежища.','Bring Ruth to the orchard and switch on the shelter light.')}
for entry in d['scenes']:
 if entry['id'] in entry_goals:entry['intent_ru'],entry['intent_en']=entry_goals[entry['id']]
d['campaign_structure']='One continuous Daniel/Mara journey; county stories are optional, not the main campaign.';d['target_playtime_hours']=[12,24];d['measured_hours']=None;d['continuation_voiceover_recorded']=True
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print('MAIN_CONTINUATION',len(d['scenes']),'scenes',sum(len(s['ru']) for s in d['scenes']),'lines per language')
