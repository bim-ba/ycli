---
source: https://yandex.ru/support/wiki/ru/wysiwyg/html-block
title: "Блок с HTML-разметкой |"
word_count: 680
token_estimate: 1995
extracted: "2026-05-13T10:28:50Z"
mode: quality
---

В [новом редакторе](https://yandex.ru/support/wiki/ru/pages-types#new-editor) можно добавить на страницу HTML-разметку с помощью специального блока. HTML-разметка позволяет создать сложную верстку: например, промо‑страницу, дизайн которой не получится реализовать стандартными элементами.

HTML-блок можно использовать вместе с другими блоками и элементами разметки на странице.

# Добавить блок

Визуальный редактор

Разметка Markdown

Чтобы добавить блок с HTML-разметкой:

1.  На панели инструментов нажмите → **HTML**.

    Вы также можете использовать меню быстрого доступа: введите символ `/` и выберите команду из списка.

2.  Внутрь блока добавьте вашу HTML-разметку и стили CSS. Например:

    ```
    <h1>Заголовок HTML-блока</h1>

    <p>Текст, размеченный с помощью HTML.</p>
    ```

Чтобы отредактировать HTML‑блок:

1.  В правом верхнем углу блока нажмите → **Редактировать**.

2.  Внесите изменения и нажмите **Сохранить**.

Чтобы удалить HTML-блок, в правом верхнем углу блока нажмите → **Удалить**.

1.  Задайте границы блока с помощью разметки:

    ```
    ::: html

    :::
    ```

2.  Внутрь блока добавьте вашу HTML-разметку и стили CSS. Например:

    ```
    ::: html

    <h1>Заголовок HTML-блока</h1>

    <p>Текст, размеченный с помощью HTML.</p>

    :::
    ```

В HTML-блоке можно использовать только разметку HTML и CSS. Разметка YFM внутри блока не поддерживается.

Больше примеров использования HTML можно найти на странице [Markdown Editor Playground](https://preview.gravity-ui.com/md-editor/?path=%2Fstory%2Fextensions-yfm--yfm-html-block).

# Использовать стили

Чтобы задать стили для элементов вашей HTML-разметки, добавьте тег `<style>` с описанием стилей CSS. Например:

```
::: html

<style>
    header {
        font-size: 100px;
    }
    .info-block {
        margin-bottom: 20px;
    }
</style>

<div class="info-block">
    <h1>Заголовок HTML-блока</h1>
</div>

:::
```

## Допустимые CSS-свойства

Ниже приведены CSS-свойства, которые можно использовать в блоке. Для удобства список отсортирован по алфавиту.

**Список CSS-свойств**

```
align-content
align-items
align-self

background
background-attachment
background-clip
background-color
background-image
background-origin
background-position
background-repeat
background-size

border
border-bottom
border-bottom-color
border-bottom-left-radius
border-bottom-right-radius
border-bottom-style
border-bottom-width
border-collapse
border-color
border-image
border-image-outset
border-image-repeat
border-image-slice
border-image-source
border-image-width
border-left
border-left-color
border-left-style
border-left-width
border-radius
border-right
border-right-color
border-right-style
border-right-width
border-spacing
border-style
border-top
border-top-color
border-top-left-radius
border-top-right-radius
border-top-style
border-top-width
border-width

box-decoration-break
box-shadow
box-sizing
box-snap
box-suppress

break-after
break-before
break-inside

color
color-interpolation-filters

column-count
column-fill
column-gap
column-rule
column-rule-color
column-rule-style
column-rule-width
column-span
column-width

columns

display
display-inside
display-list
display-outside

flex
flex-basis
flex-direction
flex-flow
flex-grow
flex-shrink
flex-wrap

font
font-family
font-feature-settings
font-kerning
font-language-override
font-size
font-size-adjust
font-stretch
font-style
font-synthesis
font-variant
font-variant-alternates
font-variant-caps
font-variant-east-asian
font-variant-ligatures
font-variant-numeric
font-variant-position
font-weight

grid
grid-area
grid-auto-columns
grid-auto-flow
grid-auto-rows
grid-column
grid-column-end
grid-column-start
grid-row
grid-row-end
grid-row-start
grid-template
grid-template-areas
grid-template-columns
grid-template-rows

height

justify-content
justify-items
justify-self

letter-spacing

lighting-color

list-style
list-style-image
list-style-position
list-style-type

margin
margin-bottom
margin-left
margin-right
margin-top

max-height
max-width

min-height
min-width

object-fit
object-position

order

orphans

padding
padding-bottom
padding-left
padding-right
padding-top

row-gap

text-align
text-align-last
text-combine-upright
text-decoration
text-decoration-color
text-decoration-line
text-decoration-skip
text-decoration-style
text-emphasis
text-emphasis-color
text-emphasis-position
text-emphasis-style
text-height
text-indent
text-justify
text-orientation
text-overflow
text-shadow
text-space-collapse
text-transform
text-underline-position
text-wrap

width

word-break
word-spacing
word-wrap
```

## CSS-переменные

HTML-блок поддерживает CSS-переменные, которые соответствуют стандартным стилям сервиса. С их помощью вы можете оформить ваш контент так же, как прочие элементы на странице. Стили, заданные с помощью CSS-переменных, будут динамически адаптироваться к смене [темы](https://yandex.ru/support/wiki/ru/wysiwyg/html-block#themes).

Чтобы использовать CSS‑переменные при объявлении стилей, в значении свойства напишите `var()`, а в скобках укажите название переменной:

```
::: html

<style>
    body {
        font-size: var(--yfm-html-font-size);
    }
</style>

:::
```

| **Переменная** | **Описание** |
| --- | --- |
| `--yfm-html-color-text-primary` | Цвет основного текста. Подходит для заголовков, абзацев и кнопок. |
| `--yfm-html-color-text-secondary` | Цвет дополнительного текста. Подходит для подписей и определений. |
| `--yfm-html-color-background` | Цвет фона. |
| `--yfm-html-color-background-secondary` | Цвет подложки для текста. |
| `--yfm-html-color-link` | Цвет ссылки. |
| `--yfm-html-color-link-hover` | Цвет ссылки при наведенном курсоре. |
| `--yfm-html-color-link-visited` | Цвет посещенной ссылки. |
| `--yfm-html-font-family` | Название шрифта. |
| `--yfm-html-font` | Тип шрифта. |
| `--yfm-html-font-size` | Размер шрифта. |
| `--yfm-html-line-height` | Высота строки. |

## Темы оформления

В сервисе доступны несколько тем оформления:

| **Тема** | **Описание** |
| --- | --- |
| `light` | Светлая |
| `light-hc` | Светлая с высокой контрастностью (beta) |
| `dark` | Темная |
| `dark-hc` | Темная с высокой контрастностью (beta) |

Чтобы ваш контент динамически адаптировался к смене темы, используйте один из вариантов:

-   [CSS‑переменные](https://yandex.ru/support/wiki/ru/wysiwyg/html-block#css-variables), которые уже поддерживают динамическое переключение между темами.

-   Задайте собственные стили для разных тем с помощью селекторов, которые содержат имя темы:

    ```
    ::: html

    <style>
        .dark-hc .section,
        .dark .section {
            background-image: url("../dark.png");
        }

        .light-hc .section,
        .light .section {
            background-image: url("../light.png");
        }

        .header {
            color: var(--yfm-html-color-text-primary)
        }
    </style>

    <div class="section">
        <h1 class="header">Заголовок</h1>
    </div>

    :::
    ```