#!/bin/python3
import math

# Constants
AU = 149597870700 # meters
L_vega = 3.0128e28 # Watts
stefan = 5.6703e-8 # Watts / (meter^2 * Kelvin^4)
parsec = AU / math.tan((math.pi/180)*(1/3600)) # 1 AU/tan(1")
F0 = L_vega / (4 * math.pi * (10*parsec)**2) # Reference Flux

def distance_modulus(inp):
  """Distance modulus calculator."""
  inp=inp.split()
  for i in range(len(inp)):
    try:
      inp[i]=float(inp[i])
    except ValueError:
      x=i
  
  m=inp[0]
  M=inp[1]
  d=inp[2]
  
  if x==0:
    return 5 * math.log10(d/10) + M
  elif x==1:
    return m - 5*math.log10(d/10)
  elif x==2:
    modulus = m - M
    result = 10 ** (modulus/5)
    result = 10 * result  #Correct the units
    return result
  else:
    raise Exception("No unknowns!")

def mag_def(inp):
  """Converts to and from flux in W/m^2 and magnitude."""
  global F0
  inp = inp.split()
  for i in range(2):
    try:
      inp[i] = float(inp[i])
    except ValueError:
      x = i
  
  m = inp[0]
  F = inp[1]
  
  if x==0:
    return -2.5 * math.log10(F/F0)
  elif x==1:
    f_vega = 10 ** ((-2)*m*(1/5))
    return f_vega * F0
  else:
    raise Exception("No unknowns!")

def difficulty(mag):
  """Returns difficulty of observation of object with given magnitude."""
  mag = float(mag)
  if mag <= -4:
    return "Visible in daytime."
  elif mag <= 6:
    return "Visible at night."
  else:
    flux = mag_def("%s x" % mag)
    needed_flux = mag_def("6 x")
    eye_area = math.pi * (0.005**2)
    needed_power = needed_flux * eye_area
    diameter = 2 * math.sqrt(needed_power / (flux*math.pi))
    return "%s m telescope needed." % diameter

def main():
  print("Type \"help\" for help.")
  while True:
    inp = input("> ")
    inp = inp.split()
    try:
      command = inp[0]
    except IndexError:
      command = "help"
    if command == "help":
      print("Commands:")
      print("help: Display help")
      print("exit: exit")
      print("mod m M d: solve the distance modulus m-M = 5*log(d/10)")
      print("mag_def magnitude flux: solve the magnitude definition")
      print("diff m: Difficulty of observing object with magnitude m")
      print("Units:")
      print("distance in parsecs.")
      print("flux in W/m^2")
    elif command == "exit":
      break
    else:
      inp = " ".join(inp[1:])
      if command == "mod":
        print(distance_modulus(inp))
      elif command == "mag_def":
        print(mag_def(inp))
      elif command == "diff":
        print(difficulty(inp))
      else:
        print("Not a valid command.")

if __name__ == "__main__":
  main()