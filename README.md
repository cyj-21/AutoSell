# auto_NTE


The two numbers are current energy and energy to keep. Rounds are calculated as `(current - keep) // 12`.

Flow: press `F` -> wait `begin` button area -> click start -> wait 50s -> click top-left exit area -> wait `finish` claim area -> click claim -> wait 3s.

Runtime screenshots are saved to `screenshout`. Move the mouse to the top-left corner to stop.

Keyboard and mouse input uses `pydirectinput`; screenshots still use `pyautogui`.

The script only checks small button regions. Existing full-screen `baseline/begin.png` and `baseline/finish.png` still work; the script crops them automatically.

You can also run without arguments and enter the two values when prompted:


