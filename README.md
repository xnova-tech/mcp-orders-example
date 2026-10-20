# MCP-сервер заказов на Python

Минимальный локальный пример **Model Context Protocol**. Сервер открывает два инструмента:
`get_order(order_id)` возвращает заказ из `orders.json`, `calculate_order_total(order_id)`
суммирует `quantity * unit_price`. Клиент обнаруживает инструменты через MCP и вызывает их
по `stdio`. Модель, токены, HTTP-сервер, Docker и платные сервисы не нужны.

Используются Python **3.11 или новее**, официальный `mcp==2.3.0` и `pydantic==2.13.5`.
Цены — целочисленные условные единицы; это не финансовая система и не образец авторизации.
Сервер **только читает** фиксированный JSON, не отправляет данные в сеть и не меняет заказы.

## Запуск

```bash
git clone https://github.com/xnova-tech/mcp-orders-example.git
cd mcp-orders-example
python -m venv .venv
```

Активируйте окружение:

- **macOS / Linux:** `source .venv/bin/activate`
- **Windows PowerShell:** `.\.venv\Scripts\Activate.ps1`
- **Windows cmd:** `.venv\Scripts\activate.bat`

Затем в той же директории:

```bash
python -m pip install -r requirements.txt
python client.py
python test_orders.py
```

Успешный `client.py` печатает названия двух инструментов, наличие двух позиций в
`ORD-101` и сумму **380**. `test_orders.py` проверяет оба существующих заказа,
схемы аргументов, неизвестный заказ, неверный ID, пропущенный или числовой аргумент
и неизвестный инструмент. Успешная проверка завершится строкой
`smoke checks passed` и кодом выхода 0. Это **ожидаемые** результаты, которые необходимо
сверить после реального запуска в вашем окружении.

`client.py` запускает `server.py` как дочерний процесс. Отдельный терминал для сервера,
ручной запуск `server.py` или открытие HTTP-порта не нужны. Запустите команды из корня
склонированного репозитория.

## Если что-то не работает

| Симптом | Что проверить |
|---|---|
| `ModuleNotFoundError: mcp` | Активировано ли `.venv`? Выполните `python -m pip install -r requirements.txt` тем же Python, которым запускаете клиент |
| Ошибка запуска дочернего процесса | Оба файла `client.py` и `server.py` должны быть в корне проекта; проверьте `python --version` |
| Нет двух инструментов | В `server.py` должны быть оба `@mcp.tool()`; в `stdout` сервера нельзя печатать обычные логи |
| Проверка суммы не прошла | Верните исходные значения `orders.json` и повторите `python test_orders.py` |
| Ошибка при активации PowerShell | Используйте `cmd` и `.venv\Scripts\activate.bat` либо настройте разрешённый способ активации в PowerShell |

Для повторного запуска после изменений данных завершите клиент и запустите его заново:
при каждом подключении он поднимает новый сервер и читает актуальный JSON.

## Как устроено

```text
client.py (MCP Client)
   | tools/list, tools/call  [stdio / JSON-RPC]
   v
server.py (MCP Server)
   | читает
   v
orders.json
```

Исходный код сервера не предоставляет доступ к произвольным файлам: путь к каталогу
фиксирован относительно `server.py`. ID заказа проверяется, ошибки операций
возвращаются как `is_error=True`, а успешные результаты содержат
`structured_content`. Это не заменяет авторизацию реального сервиса.

Референсы: [спецификация MCP](https://modelcontextprotocol.io/specification/2026-07-28),
[официальный Python SDK](https://py.sdk.modelcontextprotocol.io/),
[контракт клиента и ошибок](https://py.sdk.modelcontextprotocol.io/client/).

Автор: XNova.
