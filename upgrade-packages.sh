#!/bin/sh

set -e

if [ ! -f apk-packages.txt ]; then
  echo "Файл apk-packages.txt не найден!"
  exit 1
fi

echo "📦 Установка указанных версий пакетов..."

while IFS= read -r line || [ -n "$line" ]; do
  pkg=$(echo "$line" | xargs)  # убираем пробелы
  if [ -n "$pkg" ]; then
    echo "👉 apk add --upgrade $pkg"
    apk add --upgrade "$pkg"
  fi
done < apk-packages.txt

echo "✅ Обновление завершено."
