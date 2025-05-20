Функция для тестирования ответов на команды с сервера
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Импортируем сам модуль тестирования
    >>> from __main__ import testing, setup, terminate

Включаем сервер и подлючаемся к сокету
    >>> server, soc = setup()

Установка монстра (недалеко от начального положения игрока)
    >>> testing(soc, 'addmon hellokitty 21 0 1 "Happy python-prac exam day!"')
    'Added monster hellokitty to (1, 0) saying Happy python-prac exam day!'

Подход к монстру; ожидаемый ответ: "появление" монстра и произнесение им приветствия
    >>> testing(soc, 'move 1 0')
    'Moved to 1 0\nMoved to ...\n _____________________________ \n< Happy python-prac exam day! >\n ----------------------------- \n  \\\n   \\\n      /\\_)o<\n     |      \\\n     | O . O|\n      \\_____/'

Атака на монстра с мечом
    >>> testing(soc, 'attack hellokitty 10 sword')
    'Attacked hellokitty with sword, damage 10 hitpoints\nhellokitty now has 11 hitpoints'

Атака на монстра с топором
    >>> testing(soc, 'attack hellokitty 20 axe')
    'Attacked hellokitty with axe, hellokitty died'

Завершаем тестирование
    >>> terminate(server)
