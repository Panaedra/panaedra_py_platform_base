import string
import random
from random import randint

class sc_msrandom:

  @staticmethod
  def GetRandomStringID(size=20, chars=string.ascii_uppercase + string.digits):
    """Random id generator"""
    return ''.join(random.choice(chars) for dummy in range(size))
     
  @staticmethod
  def GetRandomInt64ID():
    """The range is max 15 digits, and therefore safe to use in _CLOUD_ as a 'score'."""
    return randint(-999999999999999,999999999999999)
   
#EOF
