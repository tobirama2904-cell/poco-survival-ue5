#!/usr/bin/env python3
"""Original authored rural story content; no generated duration estimate."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def beat(text):
 pairs=[line.split(' | ',1) for line in text.strip().splitlines()];assert all(len(p)==2 for p in pairs)
 return {'ru':[p[0] for p in pairs],'en':[p[1] for p in pairs]}
def arc(id,title,en_title,poi,a,b,read,repair,left,right):
 return {'id':id,'title':title,'title_en':en_title,'poi':poi,'choices':[a,b],'repair_cost':{'Scrap':1,'Wood':1},'beats':[beat(read),beat(repair),beat(left),beat(right)]}
arcs=[]
arcs.append(arc('last_bus','Последний автобус','The Last Bus','cedar_camp',['Передать список по радио','Broadcast the passenger list'],['Снять список с эфира','Keep the list off the air'],'''
Мара: На стекле написано: «Не заводить. Внутри спят дети». | Mara: The window says, "Do not start the engine. Children asleep inside."
Дэниел: Следов шин нет. Автобус сюда не доехал. | Daniel: There are no tyre tracks. The bus never made it here.
Мара: Значит, они написали это на окне барака. Чтобы дети продолжали верить. | Mara: Then they wrote it on the hut window. So the children could keep believing.
Дэниел: В журнале эта остановка отмечена пустой. | Daniel: The dispatch log marked this stop empty.
Мара: Тут семнадцать имён. Пустым был ваш ответ. | Mara: There are seventeen names here. It was your answer that was empty.
Дэниел: Починим передатчик. Но сначала проверим, кто слушает. | Daniel: We will fix the transmitter. First we find out who is listening.
''','''
Дэниел: Контакт держится. Этот кусок дерева из детской кровати. | Daniel: The contact holds. That brace came from a child's bed.
Мара: Не называй это вторым шансом. У кровати он был один. | Mara: Do not call this a second chance. The bed only had one.
Рут: В клинике ещё ищут родственников с той остановки. | Ruth: People at the clinic are still looking for family from that stop.
Дэниел: А по общему каналу ищут тех, у кого остались припасы. | Daniel: The public channel also has people hunting for supplies.
Рут: Я могу сверить имена лично. Это займёт время. | Ruth: I can check the names in person. It will take time.
Мара: Слева — общий эфир. Справа — снять список и отнести Рут. Решай сам. | Mara: Left is the public channel. Right takes the list offline for Ruth. You decide.
''','''
Дэниел: Красный Кедр. Семнадцать пассажиров. Я прочту каждого. | Daniel: Red Cedar. Seventeen passengers. I will read every name.
Мара: Не начинай со своей должности. Здесь она ничего не значит. | Mara: Do not begin with your job title. It means nothing here.
Рут: Первое имя совпало. Женщина у меня на кухне услышала сына. | Ruth: The first name matched. A woman in my kitchen heard her son's name.
Дэниел: Он жив? | Daniel: Is he alive?
Рут: Нет. Но сегодня она перестанет ждать автобус. | Ruth: No. But today she can stop waiting for the bus.
Мара: Сигнал заметили и заражённые. Свет у передатчика теперь выдаёт нас. | Mara: The infected noticed the signal too. The transmitter light exposes us now.
''','''
Дэниел: Передатчик останется выключенным. Имена забираю с собой. | Daniel: The transmitter stays off. I am taking the names.
Мара: Опять один человек решает, кому достанется правда. | Mara: One person deciding who gets the truth again.
Дэниел: Поэтому копия останется здесь. Не у меня в кармане. | Daniel: That is why a copy stays here. Not in my pocket.
Рут: Принесёшь оригинал — я начну поиск. Без обещаний найти всех. | Ruth: Bring the original and I will start looking. No promises of finding everyone.
Мара: В ящике остались перевязки. Возьми одну; за остальными могут вернуться. | Mara: There are dressings in the box. Take one; someone may return for the others.
Дэниел: На этот раз я оставлю им ответ, даже если он никому не понравится. | Daniel: This time I will leave an answer, even if nobody likes it.
'''))
arcs.append(arc('safe_route','Дорога без адреса','A Road Without an Address','ranger_station',['Включить общий маяк','Switch on the public beacon'],['Сохранить скрытый маршрут','Keep the route concealed'],'''
Дэниел: На карте тропа заканчивается раньше перевала. | Daniel: The trail ends before the pass on this map.
Оуэн: Не всякая оборванная линия означает обвал. | Owen: A broken line does not always mean a landslide.
Мара: Кто-то стёр дорогу наждачной бумагой. Остальные отметки целы. | Mara: Someone sanded the road away. Every other mark is intact.
Оуэн: Там прятались семьи, которым не разрешили сесть на паром. | Owen: Families hid there after they were turned away from the ferry.
Дэниел: Ты знал и продолжал брать плату за переправу? | Daniel: You knew, and kept charging for passage?
Оуэн: Я знал, что бесплатных мест меньше, чем людей. Это не оправдание. | Owen: I knew there were fewer free places than people. That is not an excuse.
''','''
Мара: У маяка сломан корпус, не лампа. Старую опору можно подпереть доской. | Mara: The beacon housing is broken, not the lamp. A plank can brace it.
Дэниел: Теперь перевал увидят с дороги. | Daniel: Now the pass can be seen from the road.
Оуэн: И с грузовиков тех, кто проверяет фамилии. | Owen: And from the trucks of people who check surnames.
Мара: Если оставить темноту, новые беглецы могут пройти мимо. | Mara: Leave it dark and new refugees may miss the way.
Дэниел: А если зажечь — у старых не останется тайника. | Daniel: Light it and the people already there lose their hiding place.
Оуэн: Ключи одинаковые. Один включает маяк. Другой запирает журнал маршрутов. | Owen: The keys are identical. One powers the beacon. The other locks away the route book.
''','''
Мара: Свет дошёл до нижнего поворота. | Mara: The light reaches the lower bend.
Дэниел: Пусть дорога снова будет дорогой, а не привилегией. | Daniel: Let it be a road again, not a privilege.
Оуэн: Красиво звучит. Ночевать возле неё придётся не тебе одному. | Owen: That sounds fine. You are not the only one who will have to sleep beside it.
Мара: Поэтому мы не пишем имена на указателе. Только направление. | Mara: That is why the sign gets a direction, not names.
Дэниел: Я оставлю предупреждение о проверках у моста. | Daniel: I will leave a warning about the bridge patrols.
Оуэн: Тогда поставь своё имя под предупреждением. Я своё тоже поставлю. | Owen: Put your name under that warning. I will put mine there too.
''','''
Дэниел: Маяк погашен. Журнал останется у людей, которые здесь живут. | Daniel: The beacon is off. The book stays with the people who live here.
Мара: Мы сохранили укрытие. Не говори, что спасли всех. | Mara: We preserved a hiding place. Do not say we saved everyone.
Оуэн: На обратном пути я оставлю тихие метки у ручья. | Owen: On the way back I will leave discreet marks beside the stream.
Дэниел: Их тоже могут прочесть не те люди. | Daniel: The wrong people can read those too.
Оуэн: Да. Безопасной дороги не было даже до конца света. | Owen: Yes. There were no perfectly safe roads before the world ended either.
Мара: Здесь есть бинт. Остальное оставим тем, кто всё-таки найдёт тропу. | Mara: There is a bandage here. We leave the rest for whoever finds the trail.
'''))
arcs.append(arc('night_watch','Чужая смена','Someone Else’s Watch','north_lookout',['Зажечь сигнальный огонь','Light the signal'],['Оставить вышку тёмной','Leave the lookout dark'],'''
Мара: На двери семь зарубок. Последняя почти у пола. | Mara: Seven marks on the door. The last is almost at floor level.
Дэниел: Человек уже не мог поднять руку. | Daniel: Whoever made it could no longer raise an arm.
Рут: Это пост Норы. Она докладывала о погоде даже после укуса. | Ruth: This was Nora's post. She reported the weather even after she was bitten.
Мара: Зачем вы оставили её одну? | Mara: Why did you leave her alone?
Рут: Она сказала, что смена пришла. По радио голос звучал спокойно. | Ruth: She said her relief had arrived. Her voice sounded calm on the radio.
Дэниел: Я тоже когда-то принял спокойный голос за доказательство. | Daniel: I once mistook a calm voice for proof too.
''','''
Рут: Под линзой она оставила запасной провод. | Ruth: She left a spare wire beneath the lens.
Мара: Контакт восстановлен. Свет можно направить к переправе. | Mara: The contact is restored. We can point the light towards the crossing.
Оуэн: Ночью по реке идут лодки без фонарей. Мы ждём их с утра. | Owen: Boats are coming downriver without lamps tonight. We have been waiting all day.
Дэниел: Свет приведёт их сюда. И приведёт сюда всё остальное. | Daniel: The light will bring them here. It will bring everything else here too.
Рут: Нора не должна решать за нас даже после смерти. | Ruth: Nora should not have to decide for us after her death.
Мара: Одна рукоять открывает шторку. Другая оставляет линзу закрытой. | Mara: One handle opens the shutter. The other leaves the lens covered.
''','''
Оуэн: Вижу огонь. Лодки получили ориентир. | Owen: I see the light. The boats have their landmark.
Дэниел: Запиши в журнал, что пост снова работает. | Daniel: Write in the log that the lookout is working again.
Рут: Я запишу, что Нору сменили. Не что всё стало хорошо. | Ruth: I will write that Nora was relieved. Not that everything is all right.
Мара: У деревьев движение. Долго здесь не задерживаемся. | Mara: Movement by the trees. We cannot stay here long.
Дэниел: Её кружку оставь на полке. | Daniel: Leave her mug on the shelf.
Рут: Она не любила, когда за неё мыли посуду. | Ruth: She hated people doing her washing-up for her.
''','''
Мара: Шторка закрыта. С дороги огня не видно. | Mara: The shutter is closed. There is no light from the road.
Оуэн: Тогда я пойду встречать лодки пешком. | Owen: Then I will walk out to meet the boats.
Дэниел: Это несколько часов по берегу. | Daniel: That is hours along the bank.
Оуэн: Знаю. Решение ещё не сделало работу за нас. | Owen: I know. Making the decision did not do the work for us.
Рут: Забери перевязку из постовой сумки. Нора велела не экономить на живых. | Ruth: Take a dressing from the watch bag. Nora said not to be stingy with the living.
Мара: Последнюю зарубку я не закрашу. Пусть следующая смена её увидит. | Mara: I will not paint over the last mark. Let the next watch see it.
'''))
arcs.append(arc('seed_debt','Долг семенами','A Debt in Seeds','orchard',['Открыть общий склад','Open the communal store'],['Скрыть запас на зиму','Conceal the winter reserve'],'''
Мара: Мама привязывала к веткам ложки. Птиц это не пугало. | Mara: Mum tied spoons to the branches. The birds were not frightened.
Дэниел: Тогда зачем? | Daniel: Why do it then?
Мара: Чтобы слышать ветер, когда она работала в погребе. | Mara: So she could hear the wind while she worked in the cellar.
Рут: На мешках свежие даты. Кто-то всё ещё ухаживает за садом. | Ruth: The sacks have recent dates. Someone is still tending the orchard.
Дэниел: Замок спилен изнутри. Они не охраняли еду. Они прятались рядом с ней. | Daniel: The lock was cut from inside. They were not guarding the food. They were hiding beside it.
Мара: Не трогай семейные таблички. Даже если не осталось семьи. | Mara: Leave the family labels alone. Even if the family is gone.
''','''
Дэниел: Вентиляция заработает, если закрепить заслонку. | Daniel: The ventilation will work if we brace the shutter.
Рут: Иначе запас сгниёт раньше первого холода. | Ruth: Otherwise the reserve will rot before the first cold spell.
Мара: На дверце два списка. Кто принёс семена и кто получил урожай. | Mara: There are two lists on the door. Who brought seeds, and who received the harvest.
Дэниел: Во втором больше фамилий. | Daniel: The second list has more names.
Мара: Так мама считала прибыль. | Mara: That was how Mum counted profit.
Рут: Общий склад поможет сейчас. Скрытый запас может пережить зиму. Не оба сразу. | Ruth: An open store helps now. A hidden reserve may survive winter. We cannot do both at once.
''','''
Мара: Я открыла ставни. Сад снова можно найти по свету. | Mara: I opened the shutters. People can find the orchard by its light again.
Дэниел: Надо установить норму выдачи. | Daniel: We should set a ration limit.
Мара: Сначала научись спрашивать, сколько людям нужно. | Mara: First learn to ask how much people need.
Рут: Оставлю здесь человека, когда смогу. Сегодня людей не хватает даже в клинике. | Ruth: I will send someone when I can. Today the clinic is short-handed too.
Дэниел: Значит, дверь будет открыта без смотрителя. | Daniel: Then the door will be open without a keeper.
Мара: Да. Доверие выглядит довольно глупо, пока кто-нибудь его не оправдает. | Mara: Yes. Trust looks rather foolish until somebody honours it.
''','''
Дэниел: Я убрал вывеску. Вентиляцию с дороги не видно. | Daniel: I took down the sign. The ventilation cannot be seen from the road.
Рут: Я отмечу запас для зимней выдачи. Не для тех, у кого есть оружие. | Ruth: I will mark the reserve for winter distribution. Not for whoever has a gun.
Мара: У моей матери не было графы «заслужил». Не добавляй её. | Mara: My mother's book had no column for "deserving". Do not add one.
Дэниел: А если кто-то голодный придёт сегодня? | Daniel: What if someone hungry comes today?
Мара: Скажем правду: мы оставили на завтра то, что могло помочь сейчас. | Mara: We tell the truth: we kept for tomorrow something that could help now.
Рут: Возьми одну перевязку из аптечки. Семена не трогай. | Ruth: Take one dressing from the first-aid box. Leave the seeds.
'''))
arcs.append(arc('room_nine','Девятая комната','Room Nine','road_house',['Открыть приют','Open the shelter'],['Оставить адрес закрытым','Keep the address private'],'''
Дэниел: На стойке книга гостей. Последние страницы вырваны. | Daniel: There is a guest book on the counter. Its last pages were torn out.
Оуэн: Их не сожгли. Смотри под ножкой стола. | Owen: They were not burned. Look beneath the table leg.
Мара: Ими выровняли мебель. Чьи-то имена перестали качать стол. | Mara: They levelled the table with them. Someone's names stopped it wobbling.
Оуэн: В девятой комнате жила моя сестра. Я сказал всем, что она уехала на восток. | Owen: My sister lived in room nine. I told everyone she had gone east.
Дэниел: А она? | Daniel: And did she?
Оуэн: Она отказалась назвать соседей. После этого я перестал писать ей письма. | Owen: She refused to name her neighbours. After that I stopped writing to her.
''','''
Мара: Проводка цела до стойки. Дальше кто-то выдрал выключатель. | Mara: The wiring reaches the counter. Someone ripped out the switch beyond it.
Дэниел: Поставлю новый контакт. Не трогай оголённый конец. | Daniel: I will fit a new contact. Keep clear of the bare end.
Оуэн: Если зажечь знак, приют увидят с шоссе. | Owen: If we light the sign, the shelter will be visible from the highway.
Мара: Вместе с теми, кто не хочет, чтобы его нашли. | Mara: Along with people who do not want to be found.
Оуэн: Я не прошу сделать мой старый выбор правильным. | Owen: I am not asking you to make my old choice right.
Дэниел: Открыть адрес всем или оставить его тем, кто уже здесь. Я понял. | Daniel: Open the address to everyone, or leave it to those already here. I understand.
''','''
Оуэн: Вывеска горит. Я забыл, какого она была цвета. | Owen: The sign is lit. I had forgotten its colour.
Мара: Твоя сестра могла бы сердиться. | Mara: Your sister might be angry.
Оуэн: Могла бы. Она умела делать сразу несколько вещей. | Owen: She might. She could do several things at once.
Дэниел: На входе оставлю правило: никаких списков фамилий. | Daniel: I will leave a rule at the door: no lists of surnames.
Мара: Правило на бумаге никого не остановит само по себе. | Mara: A rule on paper will not stop anyone by itself.
Оуэн: Тогда начнём с меня. Здесь я больше не беру плату. | Owen: Then start with me. I no longer charge here.
''','''
Дэниел: Вывеска останется погашенной. | Daniel: The sign stays dark.
Оуэн: А книгу гостей оставь открытой на пустой странице. | Owen: Leave the guest book open at a blank page.
Мара: Для новых имён? | Mara: For new names?
Оуэн: Нет. Чтобы входящий видел: писать ничего не нужно. | Owen: No. So anyone entering can see there is nothing to write.
Рут: В шкафу есть перевязки. Одну возьми в дорогу, остальные оставь постояльцам. | Ruth: There are dressings in the cupboard. Take one for the road; leave the rest for the guests.
Дэниел: Девятую комнату я не запру. | Daniel: I will not lock room nine.
'''))
arcs.append(arc('open_frequency','Открытая частота','An Open Frequency','relay_camp',['Включить открытый канал','Open the public channel'],['Оставить направленный канал','Keep the directed channel'],'''
Мара: Вот запись того приказа. Без обрезанного начала. | Mara: Here is the recording of that order. With the beginning intact.
Дэниел: Я помню каждое слово. | Daniel: I remember every word.
Мара: Тогда почему ты всегда начинаешь со второго предложения? | Mara: Then why do you always start with the second sentence?
Дэниел: В первом я спросил, подтверждено ли заражение. Мне не ответили. | Daniel: In the first, I asked whether infection had been confirmed. Nobody answered.
Мара: И ты всё равно передал приказ. | Mara: And you transmitted the order anyway.
Дэниел: Да. Запись не оправдывает меня. Она только перестаёт быть удобной. | Daniel: Yes. The recording does not excuse me. It only stops being convenient.
''','''
Дэниел: Усилитель держит ток. Теперь можно выбрать антенну. | Daniel: The amplifier holds its charge. Now we can choose the antenna.
Мара: Открытый канал услышат все, кто ещё слушает. | Mara: Everyone still listening will hear the public channel.
Рут: В том числе те, кто ждёт повода выгнать чужих из клиники. | Ruth: Including people waiting for an excuse to drive outsiders from the clinic.
Оуэн: Направленный канал дойдёт до переправы. Там решат, что передать дальше. | Owen: The directed channel reaches the ferry. They will decide what to pass on.
Мара: Я хотела, чтобы ты признался. А теперь мне страшно от того, кто это услышит. | Mara: I wanted you to admit it. Now I am afraid of who will hear.
Дэниел: Страх не исчезнет после нажатия. Ни у одного из нас. | Daniel: Pressing a switch will not take away the fear. Not for either of us.
''','''
Дэниел: Меня зовут Дэниел Рид. Я передал приказ, не получив подтверждения. | Daniel: My name is Daniel Reed. I transmitted an order without receiving confirmation.
Мара: Не обещай, что больше никогда не ошибёшься. | Mara: Do not promise you will never make another mistake.
Дэниел: Не обещаю. Дальше в записи есть имена тех, кто пытался меня остановить. | Daniel: I will not. The recording also names people who tried to stop me.
Рут: Канал занят. Люди отвечают друг другу, не тебе. | Ruth: The channel is busy. People are answering one another, not you.
Дэниел: Так и должно быть. | Daniel: That is how it should be.
Мара: Оставь микрофон включённым. Теперь наша очередь слушать. | Mara: Leave the microphone on. It is our turn to listen.
''','''
Дэниел: Запись ушла на переправу. Без правок. | Daniel: The recording went to the ferry. Unedited.
Мара: Но не всем. Эту часть тоже запомни. | Mara: But not to everyone. Remember that part too.
Оуэн: Я сделаю копии. И не стану говорить, будто получил их случайно. | Owen: I will make copies. I will not pretend I received them by accident.
Дэниел: Одну оставим здесь, рядом с передатчиком. | Daniel: We leave one here beside the transmitter.
Рут: В дороге понадобится перевязка. В соседнем ящике есть запасная. | Ruth: You will need a dressing on the road. There is a spare in the next box.
Мара: Я всё ещё злюсь. Но хотя бы знаю, на кого, а не на запись чужого голоса. | Mara: I am still angry. At least I know with whom, instead of with a recording of a stranger's voice.
'''))
d={'schema':1,'arc_title':{'ru':'Те, кого не записали','en':'The Uncounted'},'setting':'Original Bellwether County, Oregon narrative; not a TLOU retelling.','arcs':arcs,'measured_playtime_hours':None,'new_dialogue_voiceover_complete':False}
(ROOT/'BuildData/story/county-stories.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print('AUTHORED_COUNTY_STORIES',len(arcs),sum(len(b['ru']) for a in arcs for b in a['beats']))
