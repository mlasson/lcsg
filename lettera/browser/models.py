from django.db import models

# Create your models here.

word_size = 50
letter_size = 50000


class Period(models.Model):
    start = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)
    name = models.CharField(max_length=word_size)
    size = models.IntegerField(default=0)

    def __str__(self):
        return '{0} : {1} - {2}'.format(self.name, self.start, self.end)


class Letter(models.Model):
    number = models.IntegerField(default=0)
    volume = models.IntegerField(default=0)
    period = models.ForeignKey(
        Period, null=True, blank=True, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    text = models.TextField()
    author = models.CharField(max_length=word_size)
    ignore = models.BooleanField(default=False)

    def __str__(self):
        return '{0} volume {1}'.format(self.number, self.volume)


class Family(models.Model):
    name = models.CharField(max_length=word_size)
    df = models.IntegerField(default=0)
    idf = models.FloatField(default=0.0)

    def __str__(self):
        return self.name


class Word(models.Model):
    name = models.CharField(max_length=word_size)
    family = models.ForeignKey(Family, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('name', )

    def __str__(self):
        return self.name


class Sentence(models.Model):
    letter = models.ForeignKey(Letter, on_delete=models.CASCADE)
    start_position = models.IntegerField(default=0)
    end_position = models.IntegerField(default=0)

    def __str__(self):
        return '{0} : {1} - {2}'.format(
            str(self.letter), self.start_position, self.end_position)


class Occurrence(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    letter = models.ForeignKey(Letter, on_delete=models.CASCADE)
    sentence = models.ForeignKey(Sentence, on_delete=models.CASCADE)
    start_position = models.IntegerField(default=0)
    end_position = models.IntegerField(default=0)

    def __str__(self):
        return '{0}@{1}+{2}'.format(self.word, str(self.letter),
                                    self.start_position)


class Frequency(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    letter = models.ForeignKey(Letter, on_delete=models.CASCADE)
    raw = models.FloatField(default=0.0)
    logarithmic = models.FloatField(default=0.0)
    augmented = models.FloatField(default=0.0)


class Tag(models.Model):
    occurrence = models.ForeignKey(Occurrence, on_delete=models.CASCADE)
    name = models.CharField(max_length=word_size)

    def __str__(self):
        return '{0}({1})'.format(self.name, str(self.occurrence))


class Subcorpus(models.Model):
    name = models.TextField()
    letters = models.TextField()

    def __str__(self):
        return '{0}({1})'.format(self.name, str(self.letters))


class Cache(models.Model):
    name = models.TextField()
    args = models.TextField()
    value = models.TextField()

    def __str__(self):
        return '{0}({1})'.format(self.name, self.args)
