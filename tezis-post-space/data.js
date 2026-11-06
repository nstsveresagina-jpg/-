// Содержание шпаргалок: подпись + параметры отрисовки комнаты (room.js)
const A = '#6B4535', BG = '#EBDCCB';
window.SETS = [
  { n: '02', kick: 'Цвет', title: 'Как цвет <span>меняет</span><br>пространство',
    sub: 'Ниже, шире или короче - одной только покраской.',
    items: [
      ['уменьшить', { wall: A, ceil: A }], ['укоротить', { back: A }], ['сузить', { left: A, right: A }],
      ['занизить', { ceil: A }], ['сделать уютнее', { back: A, ceil: A }], ['расширить', { band: true }],
      ['выделить зону', { panel: A }], ['повысить', { stripesAll: true }], ['увеличить', { wall: '#F2EDE5', ceil: '#F7F3EE' }],
    ] },
  { n: '03', kick: 'Оттенки', title: 'Как оттенки<br>меняют <span>атмосферу</span>',
    sub: 'Тёплые оттенки добавляют уюта, холодные&nbsp;- строгости и прохлады.',
    items: [
      ['уютнее', { wall: '#D9B79C' }], ['прохладнее', { wall: '#A7B2BB' }], ['спокойнее', { wall: '#B7BA98' }],
      ['теплее', { wall: '#C98F6E' }], ['строже', { wall: '#808487' }], ['мягче', { wall: '#DABAAF' }],
      ['глубже', { wall: '#6F735A' }], ['светлее', { wall: '#EEE6D8' }], ['выразительнее', { wall: '#7A3B35' }],
    ] },
  { n: '04', kick: 'Линии и рисунок', title: 'Как линии<br>меняют <span>комнату</span>',
    sub: 'Вертикали тянут потолок вверх, горизонтали раздвигают стены.',
    items: [
      ['вертикали', { pattern: 'vlines' }], ['горизонтали', { pattern: 'hlines' }], ['широкие полосы', { pattern: 'wide', patBg: BG }],
      ['узкие полосы', { pattern: 'narrow', patBg: BG }], ['диагонали', { pattern: 'diag', patBg: BG }], ['крупный рисунок', { pattern: 'shapes', patBg: BG }],
      ['мелкий рисунок', { pattern: 'small', patBg: BG }], ['рейки', { pattern: 'slats' }], ['молдинги', { pattern: 'mould' }],
    ] },
  { n: '05', kick: 'Свет', title: 'Как свет <span>меняет</span><br>пространство',
    sub: 'Несколько сценариев света делают комнату объёмной.',
    items: [
      ['подсветка потолка', { light: 'cove', sun: false }], ['свет вдоль стен', { light: 'wash', sun: false }], ['боковой свет', { light: 'side', sun: false }],
      ['верхний свет', { light: 'top', sun: false }], ['нижняя подсветка', { light: 'floor', sun: false }], ['акцентный свет', { light: 'accent', sun: false }],
      ['рассеянный свет', { light: 'diffuse' }], ['тёплый свет', { light: 'warm' }], ['холодный свет', { light: 'cold' }],
    ] },
  { n: '06', kick: 'Шпаргалка', title: '9 приёмов <span>визуально</span><br>увеличить комнату',
    sub: 'Сохраните, чтобы не потерять, когда начнёте ремонт.',
    items: [
      ['светлый потолок', { wall: '#DFD0BF', ceil: '#FBF8F4' }], ['акцентная стена', { back: '#A9AD8A' }], ['зеркала', { pattern: 'mirror' }],
      ['вертикальные линии', { pattern: 'slats', patColor: '#D8C4AE' }], ['горизонт. линии', { pattern: 'hlines', patColor: '#DCCAB6' }], ['высокие шторы', { curtains: true }],
      ['светлые оттенки', { wall: '#F0EAE1' }], ['подсветка периметра', { light: 'cove', sun: false }], ['единый пол', { door: true }],
    ] },
];
window.HERO = { back: '#B9A48E', cove: true };
