import tkinter as tk
from tkinter import *
from tkinter.ttk import *

import json
import git
import os
import string
import random

from dotenv import load_dotenv
load_dotenv()

# Initializes repository from the Master Tree
repo = git.Repo()
try:
	remote = repo.create_remote('origin', url='https://github.com/Kelutral-org/minecraft-translation')
except git.exc.GitCommandError as error:
	print(f'Error creating remote: {error}')

try:
	repo.remotes.origin.pull(rebase=True)
except Exception as e:
	print(f'Error creating remote: {e}')

if os.path.exists('.env'):
	branch_name = os.environ.get('BRANCH')
else:
	branch_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
	repo.create_head(branch_name)
	with open('.env', 'w') as fh:
		fh.write(f'BRANCH = {branch_name}')

refspec = f'refs/heads/{branch_name}:refs/heads/{branch_name}'

branch = repo.heads[branch_name]
branch.checkout()

masterIndex = 0
masterMode = 0

with open('nv_pn.json', 'r', encoding='utf-8') as fh:
	nv_pn = json.load(fh)
	nv_keylist = list(nv_pn.keys())

with open('en_us.json', 'r', encoding='utf-8') as fh:
	en_us = json.load(fh)
	en_keylist = list(en_us.keys())

def countToDo():
	completed = 0
	to_do = 0
	for key, value in nv_pn.items():
		try:
			current = en_us[key]
			if current != value:
				completed += 1
			else:
				to_do += 1
		except KeyError:
			continue

	with open('README.md', 'r', encoding='utf-8') as fh:
		readme = fh.readlines()

	readme[10] = f"This project is currently {round((completed / (to_do + completed)) * 100, 2)}% complete as of the most recent merge."

	with open('README.md', 'w', encoding='utf-8') as fh:
		fh.writelines(readme)

	return f"Translation project {round((completed / (to_do + completed)) * 100, 2)}% complete! {to_do} lines remaining."

window = Tk()
window.title('Kelutral.org Minecraft Translation Assistant')
window.geometry("600x300")

# Header Text
header = Label(master=window, text="Minecraft nìNa'vi")
subheader = Label(master=window, text=countToDo())

header.pack(anchor='n')
subheader.pack()

# Display Frame
disp = Frame(master=window, padding=20)
disp.pack()

def validate():
	global masterIndex
	current = nv_pn[nv_keylist[masterIndex]]
	try:
		master = en_us[nv_keylist[masterIndex]]
	except KeyError:
		nv_pn.pop(nv_keylist[masterIndex])
		master = None

	if master != None:
		if current == master:
			return ('#000000', False)
		else:
			return ('#38761d', True)
	else:
		return ('#acacac', False)

editing = Label(master=disp, text=f"Currently Editing: {nv_keylist[masterIndex]}", wraplength=500)
value = Label(master=disp, text=f"Value: {nv_pn[nv_keylist[masterIndex]]}", wraplength=500)
value.config(foreground=validate()[0])
original_value = Label(master=disp, text=f"Original Value: {en_us[nv_keylist[masterIndex]]}", wraplength=500)

editing.pack()
value.pack()
original_value.pack()

# Entry Frame
entry = Frame(master=window)
entry.pack()

def updateCallback():
	global masterIndex
	nv_pn[nv_keylist[masterIndex]] = newText.get()
	value['text'] = f"Value: {nv_pn[nv_keylist[masterIndex]]}"
	original_value['text'] = f"Original Value: {en_us[nv_keylist[masterIndex]]}"

	original_value.pack()
	value.config(foreground=validate()[0])
	disp.update_idletasks()

newText = Entry(master=entry, width=60)
submit = Button(master=entry, text="Update", command=updateCallback)

newText.pack(side = 'left', padx=5)
submit.pack(side = 'left', padx=5)

# Cycle Frame
cycle = Frame(master=window, padding=0)
cycle.pack()

def cycleLeft():
	global masterIndex
	masterIndex -= 1

	if masterMode == 1:
		while not validate()[1]:
			if masterIndex > 0:
				masterIndex -= 1
			else:
				masterIndex = len(nv_keylist) - 1

		original_value.pack()

	elif masterMode == 2:
		while validate()[1]:
			if masterIndex > 0:
				masterIndex -= 1
			else:
				masterIndex = len(nv_keylist) - 1
		
		original_value.pack_forget()
	else:
		if validate()[1]:
			original_value.pack()
		else:
			original_value.pack_forget()

	editing['text'] = f"Currently Editing: {nv_keylist[masterIndex]}"
	value['text'] = f"Value: {nv_pn[nv_keylist[masterIndex]]}"
	original_value['text'] = f"Original Value: {en_us[nv_keylist[masterIndex]]}"

	value.config(foreground=validate()[0])
	newText.delete(0, tk.END)
	disp.update_idletasks()

def cycleRight():
	global masterIndex
	masterIndex += 1

	if masterMode == 1:
		while not validate()[1]:
			if masterIndex < len(nv_keylist) - 1:
				masterIndex += 1
			else:
				masterIndex = 0

		original_value.pack()

	elif masterMode == 2:
		while validate()[1]:
			if masterIndex < len(nv_keylist) - 1:
				masterIndex += 1
			else:
				masterIndex = 0
		original_value.pack_forget()
	else:
		if validate()[1]:
			original_value.pack()
		else:
			original_value.pack_forget()

	editing['text'] = f"Currently Editing: {nv_keylist[masterIndex]}"
	value['text'] = f"Value: {nv_pn[nv_keylist[masterIndex]]}"
	original_value['text'] = f"Original Value: {en_us[nv_keylist[masterIndex]]}"

	value.config(foreground=validate()[0])
	newText.delete(0, tk.END)
	disp.update_idletasks()

cycleLeft = Button(master=cycle, text="Previous", command=cycleLeft)
cycleRight = Button(master=cycle, text="Next", command=cycleRight)

cycleLeft.pack(side = 'left', padx=5)
cycleRight.pack(side = 'left', padx=5)

mode = Frame(master=window, padding=10)
mode.pack()

Label(master=mode, text="Editing Mode:").pack(side='left')

options = [
	"View All",
	"View All",
	"Proofreading",
	"Translating"
]

clicked = StringVar(mode)

def dropdownCallback(val):
	global masterMode
	masterMode = options.index(val) - 1 if options.index(val) != 0 else options.index(val)

drop = OptionMenu(mode, clicked, *options, command=dropdownCallback)
drop.pack(side='left')

footer = Frame(master=window, padding=10)
footer.pack()

def saveCallback():
	with open('nv_pn.json', 'w', encoding='utf-8') as fh:
		json.dump(nv_pn, fh, indent=4, ensure_ascii=False)

	repo.index.add('nv_pn.json')
	repo.index.add('README.md')
	repo.index.commit(f"Submitted edits to nv_pn.json for review")
	try:
		repo.remotes.origin.push(refspec)
	except Exception as e:
		print(f'Error: {e}')

	window.destroy()

Button(master=footer, text="Save and Quit", command=saveCallback).pack(anchor='se', side='bottom')

window.mainloop()