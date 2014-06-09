from django.db import models

# Create your models here.

word_size = 50
letter_size = 50000

class Period(models.Model):
  start = models.DateField(null=True, blank=True)
  end = models.DateField(null=True, blank=True)
  name = models.CharField(max_length=word_size)
 
  def __str__(self):
    return '{0} : {1} - {2}'.format(self.name, self.start, self.end)


class Letter(models.Model):
  number = models.IntegerField(default=0)
  volume = models.IntegerField(default=0)
  period = models.ForeignKey(Period, null=True, blank=True)
  date = models.DateField(null=True, blank=True)
  text = models.TextField()
  author = models.CharField(max_length=word_size)

  def __str__(self):
    return '{0} volume {1}'.format(self.number, self.volume)


class Family(models.Model):
  name = models.CharField(max_length=word_size)

  def __str__(self):
    return self.name


class Word(models.Model):
  name = models.CharField(max_length=word_size)
  family = models.ForeignKey(Family)

  class Meta:
    unique_together = ('name',)

  def __str__(self):
    return self.name


class Occurrence(models.Model):
  word = models.ForeignKey(Word)
  letter = models.ForeignKey(Letter)
  start_position = models.IntegerField(default=0)
  end_position = models.IntegerField(default=0)

class Cache(models.Model):
  name = models.TextField()
  args = models.TextField()
  value = models.TextField()
  
  def __str__(self):
    return '{0}({1})'.format(self.name, self.args)
