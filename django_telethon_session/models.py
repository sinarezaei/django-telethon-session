from django.db import models


class TelethonSession(models.Model):
    dc_id = models.IntegerField(primary_key=True, null=False, blank=False)
    server_address = models.CharField(max_length=1000, blank=True, null=True)
    port = models.IntegerField(blank=True, null=True)
    auth_key = models.BinaryField(blank=False, null=False)
    takeout_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.dc_id) + '_' + str(self.server_address) + '_' + str(self.port)

    def __repr__(self):
        return self.__str__()

    def get_as_rows(self):
        return [self.dc_id, self.server_address, self.port, self.auth_key, self.takeout_id]


class TelethonEntity(models.Model):
    identifier = models.IntegerField(primary_key=True, blank=False, null=False)
    hash = models.IntegerField(blank=False, null=False)
    username = models.CharField(max_length=1000, blank=True, null=True)
    phone = models.CharField(max_length=1000, blank=True, null=True)
    name = models.CharField(max_length=1000, blank=True, null=True)

    def get_as_rows(self):
        return [self.identifier, self.hash, self.username, self.phone, self.name]


class TelethonSentFile(models.Model):
    class Meta:
        unique_together = (("md5_digest", "file_size", "file_type"),)

    identifier = models.IntegerField(primary_key=True, blank=False, null=False)
    md5_digest = models.BinaryField(blank=False, null=False)
    file_size = models.IntegerField(blank=True, null=True)
    file_type = models.IntegerField(blank=True, null=True)
    file_id = models.IntegerField(blank=True, null=True)
    hash = models.IntegerField(blank=True, null=True)


class TelethonUpdateState(models.Model):
    identifier = models.IntegerField(primary_key=True, blank=False, null=False)
    pts = models.IntegerField(blank=True, null=True)
    qts = models.IntegerField(blank=True, null=True)
    date = models.IntegerField(blank=True, null=True)
    seq = models.IntegerField(blank=True, null=True)