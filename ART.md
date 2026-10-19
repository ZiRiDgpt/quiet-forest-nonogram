# Рисованный лес и белка — первая связанная пара ресурсов

Изображения созданы встроенным инструментом генерации изображений. Исходные SVG сохранены. Файлы игры: `assets/forest-painted-v1.png` (2042×770), `assets/squirrel-painted-v1.png` (512×512, RGBA). Исходная генерация белки: `assets/source/squirrel-generated-v1.png`.

## Промпты генерации

### Лес (фон непрозрачный)

Use case: illustration-story. Generate a production game background for a gentle woodland nonogram game, a richly hand-painted storybook gouache forest, mossy sage greens, warm cream sunlight, muted russet accents, soft paper texture, detailed organic trees and ferns, welcoming quiet magical atmosphere. Wide landscape composition about 2.65:1, full bleed no text/UI/borders. A forest clearing with winding path in center into misty distance; foreground old oak trunk on LEFT and an empty substantial horizontal branch extending from the left trunk into the center at about 43 percent width and 44 percent height, with clear soft light negative space immediately above it reserved for a separately composited squirrel. An empty perch toward upper right (72 percent width,37 percent height) for an owl. Ground moss patches bottom left (30percent,77percent) for a mushroom and bottom right (80percent,78percent) for hedgehog. No animals, no squirrel, no mushrooms; those will be added as independent sprites. Clear distinct depth layers and natural painted shapes, not simple geometric vector art. Maintain readability when displayed 1160 by436.

### Белка (прозрачный фон)

Use case illustration-story. Production standalone game sprite, ONE charming red squirrel in profile facing LEFT, seated upright on its haunches, both paws holding a small acorn close to chest, compact rounded body, two subtly pointed ears, enormous unmistakable fluffy curled tail rising behind its back on the RIGHT. Full entire animal incl feet and tail in frame, centered with uniform 8 percent transparent margin in a square canvas. Genuine transparent alpha background, no ground, no branch, no landscape, no drop shadow, no border or text. Rich hand-painted storybook gouache illustration, organic brush texture, quiet woodland palette: warm muted russet cinnamon fur, cream belly, dark brown tiny eye, moss-green reflected light and warm soft sunlight from upper left. Beautiful detailed painted fur within strong simple readable outer silhouette. Silhouette should still read clearly when sampled to a 15x15 monochrome nonogram: connected broad shapes, no thin whiskers, no separated tiny parts, no fragile extended limbs. Keep the tail visually distinct by a broad concave notch from the head/neck, all body parts connected. Flat side-view 2D illustration, natural woodland storybook aesthetic, not geometric vector art, not 3D, not pixel art.

## Преобразование в головоломку

`python tools/prepare-squirrel.py assets/source/squirrel-generated-v1.png` обрезает прозрачные поля и вписывает рисунок в квадрат 512×512 с сохранением пропорций и прозрачности. Рабочий кадр содержит белку максимум 444×444. Альфа-канал усредняется по клеткам 15×15 (BOX); цветные детали намеренно не участвуют, поскольку нужна узнаваемая внешняя форма.

`node tools/select-squirrel-grid.js` передаёт чёрный силуэт с полученными значениями прозрачности в существующий `NonogramCore.pixelsToGrid`. Порог 128 сразу дал единственное решение. Матрица не исправлялась вручную. `data/squirrel-painted-grid.json` фиксирует порог и сетку; `data/squirrel-sampled-rgba.json` хранит входные данные конвертера. Отдельный тест сверяет матрицу с преобразованием и повторно проверяет единственность. Единственность проверена полным решателем; отдельная оценка сложности и запрета перебора пока не выполнялась.

Изображение в RewardArt использует тот же квадрат и те же пропорции, что и матрица. При победе клетки перемещаются в квадрат 330×330 и плавно уступают место соответствующей иллюстрации. Тот же PNG используется в Reward и Discovery_squirrel. При смене SVG-заглушки на PNG сохраняются заданные ширина и высота, чтобы разница исходных разрешений не меняла размер находки.

`tools/install-painted-demo.py` подключает пару ресурсов и заменяет поле белки на 15×15; перед изменениями делает копию проекта. Другие сцены и элементы управления сохраняются. `data/art-manifest.json` задаёт используемые изображения для будущей генерации проекта.

## Проверка

16 автоматических тестов прошли; проверены матрица по силуэту, единственность решения, все четыре игровых цикла и окружение Electron. Экспорт GDevelop выполнен успешно. В экспортированной игре вручную через автоматизированные клики пройдена белка, показана награда, выполнен переход в лес. После исправления масштаба проверено сохранённое открытие при перезагрузке. Снимок: `validation/painted-forest-playtest.png`. Сцена белки проверена валидатором: 290 экземпляров, 0 ошибок и предупреждений.

Другие объекты пока используют старую временную графику. Фото-мастерская пока не перенесена. Рисованный лес сейчас единый фон, без параллакса.
