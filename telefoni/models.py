# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Contrattotelefonico(models.Model):
    numero = models.CharField(primary_key=True, max_length=20)
    dataattivazione = models.DateField(db_column='dataAttivazione')
    tipo = models.CharField(max_length=8)
    minutiresidui = models.IntegerField(db_column='minutiResidui', blank=True, null=True)
    creditoresiduo = models.DecimalField(db_column='creditoResiduo', max_digits=10, decimal_places=2, blank=True,
                                         null=True)
    nominativo = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'contrattotelefonico'

    def __str__(self):
        return f"{self.numero} - {self.nominativo or 'Senza nome'}"

class Simattiva(models.Model):
    codice = models.CharField(primary_key=True, max_length=20)
    tiposim = models.CharField(db_column='tipoSIM', max_length=20)  # Field name made lowercase.
    associataa = models.CharField(db_column='associataA', max_length=20, blank=True, null=True)  # Field name made lowercase.
    dataattivazione = models.DateField(db_column='dataAttivazione')  # Field name made lowercase.

    def __str__(self):
        return f"SIM {self.codice} - {self.associataa or 'non associata'}"
    class Meta:
        managed = True
        db_table = 'simattiva'


class Simdisattiva(models.Model):
    codice = models.CharField(primary_key=True, max_length=20)
    tiposim = models.CharField(db_column='tipoSIM', max_length=20)  # Field name made lowercase.
    eraassociataa = models.CharField(db_column='eraAssociataA', max_length=20, blank=True, null=True)  # Field name made lowercase.
    dataattivazione = models.DateField(db_column='dataAttivazione')  # Field name made lowercase.
    datadisattivazione = models.DateField(db_column='dataDisattivazione')  # Field name made lowercase.

    def __str__(self):
        return f"SIM {self.codice} - {self.eraassociataa or 'non era associata'}"
    class Meta:
        managed = True
        db_table = 'simdisattiva'


class Simnonattiva(models.Model):
    codice = models.CharField(primary_key=True, max_length=20)
    tiposim = models.CharField(db_column='tipoSIM', max_length=20)  # Field name made lowercase.

    def __str__(self):
        return f"SIM {self.codice} - {self.codice or 'senza codice'}"

    class Meta:
        managed = True
        db_table = 'simnonattiva'


class Telefonata(models.Model):
    effettuatada = models.ForeignKey(
        Contrattotelefonico,
        on_delete=models.CASCADE,
        db_column='effettuataDa',
        to_field='numero',
        null=True,
        blank=True
    )
    data = models.DateField()
    ora = models.TimeField()
    durata = models.IntegerField()
    costo = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = True
        db_table = 'telefonata'

    def __str__(self):
        return f"Telefonata del {self.data} alle {self.ora}"
