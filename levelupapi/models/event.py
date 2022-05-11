from django.db import models

class Event(models.Model):
    game = models.ForeignKey("Game", on_delete=models.CASCADE, related_name='events')
    # q for text, date, and time field options
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    organizer = models.ForeignKey("Gamer", on_delete=models.CASCADE)
    attendees = models.ManyToManyField("Gamer", 
                                       through="EventGamer", 
                                       related_name="events")
    
    @property
    def joined(self):
        return self.__joined

    @joined.setter
    def joined(self, value):
        self.__joined = value