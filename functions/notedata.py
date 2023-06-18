# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

# -------------------- Notelist --------------------

class NoteList:
  def __init__(self, timetype):
    self.data = []
    self.timetype = timetype

  def add(self, in_pos, in_dur, in_key, *args, **kwargs):
    note = {}
    note['position'] = in_pos
    note['duration'] = in_dur
    note['key'] = in_key
    for argname in kwargs:
      note[argname] = kwargs[argname]
    self.data.append(note)

  def move(self, pos):
    for note in self.data:
      note['position'] += pos

  def move_delzero(self, pos):
    newdata = []
    for note in self.data:
      newnote = note.copy()
      newnote['position'] += pos
      if newnote['position'] >= 0: newdata.append(newnote)
    self.data = newdata

  def trim(self, pos):
    newdata = []
    for note in self.data:
      if note['position'] < pos: newdata.append(note)
    self.data = newdata

  def trimmove(self, startat, endat):
    self.trim(endat)
    self.move_delzero(-startat)

  def duration(self):
    duration_final = 0
    for note in self.data:
      noteendpos = note['position']+note['duration']
      if duration_final < noteendpos: duration_final = noteendpos
    return duration_final

  def get(self):
    t_data_bsort = {}
    t_data_sorted = {}
    mulval = 1
    if self.timetype == 'steps': mulval = 1
    elif self.timetype == 'beats': mulval = 0.25
    new_data = []
    for note in self.data:
      if note['position'] not in t_data_bsort:
        t_data_bsort[note['position']] = []
      t_data_bsort[note['position']].append(note)
    t_data_sorted = dict(sorted(t_data_bsort.items(), key=lambda item: item[0]))
    for t_notepos in t_data_sorted:
      for note in t_data_sorted[t_notepos]:
        if mulval != 1:
          note['duration'] /= mulval
          note['position'] /= mulval
        new_data.append(note)
    return new_data

# -------------------- NoteMod --------------------

class NoteMod:
  def __init__(self):
    self.data = {}
    self.pitchpoints = []
    self.pitch_cur = 0
    self.pitch_prev = 0
    self.slide_zeropospointexist = False

  def pitchmod2point(self, position, ptype, maindur, slideparam, input_pitch):
    mainslideparam_mul = slideparam*maindur
    pitch_exact = False

    if 'notemod' not in self.data: self.data = {}
    if 'auto' not in self.data: self.data['auto'] = {}
    if 'pitch' not in self.data['auto']: self.data['auto']['pitch'] = []
    
    self.pitchpoints = self.data['auto']['pitch']

    if ptype == 0:
      if slideparam <= maindur:
        self.pitch_cur += input_pitch
        self.pitchpoints.append({'position': position, 'value': self.pitch_prev})
        self.pitchpoints.append({'position': position+slideparam, 'value': self.pitch_cur})
      elif slideparam > maindur:
        self.pitch_cur = xtramath.betweenvalues(self.pitch_prev, self.pitch_prev+input_pitch, maindur/slideparam)
        self.pitchpoints.append({'position': position, 'value': self.pitch_prev})
        self.pitchpoints.append({'position': position+maindur, 'value': self.pitch_cur})

    elif ptype == 1:
      input_pitch -= self.data['key']

      outdur = maindur
      if self.pitch_cur < input_pitch:
        self.pitch_cur += (mainslideparam_mul)
        pitch_exact = input_pitch < self.pitch_cur
        if pitch_exact == True: outdur = (mainslideparam_mul-(self.pitch_cur-input_pitch))/slideparam

      elif self.pitch_cur > input_pitch:
        self.pitch_cur -= (mainslideparam_mul)
        pitch_exact = input_pitch > self.pitch_cur
        if pitch_exact == True: outdur = (mainslideparam_mul+(self.pitch_cur-input_pitch))/slideparam

      if pitch_exact == True: self.pitch_cur = input_pitch

      totalslidedur = outdur/maindur

      if totalslidedur > 0.1:
        self.pitchpoints.append({'position': position, 'value': self.pitch_prev})
        self.pitchpoints.append({'position': position+(totalslidedur), 'value': self.pitch_cur})
      else:
        self.pitchpoints.append({'position': position, 'value': self.pitch_cur, 'type': 'instant'})

    elif ptype == 2:
      if self.slide_zeropospointexist == False:
        self.pitchpoints.append({'position': 0, 'value': 0})
        self.slide_zeropospointexist = True
      if slideparam != 0:
        self.pitchpoints.append({'position': position, 'value': self.pitch_cur})
        if slideparam > maindur:
          self.pitchpoints.append({'position': position+maindur, 'value': input_pitch*(maindur/slideparam)})
          self.pitch_cur = input_pitch*(maindur/slideparam)
        else:
          self.pitchpoints.append({'position': position+slideparam, 'value': input_pitch})
          self.pitch_cur = input_pitch
      else:
        self.pitchpoints.append({'position': position, 'value': input_pitch, 'type': 'instant'})
        self.pitch_cur = input_pitch

    self.pitch_prev = self.pitch_cur