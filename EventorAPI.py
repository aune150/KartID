import requests as req
import json
from datetime import datetime, date, timedelta
import xmltodict
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

@dataclass
class Lop:
    eventorID: str = ""
    navn: str = ""
    datoer: list[date] = field(default_factory=list)


class Resultat:
    def __init__(self, xml) -> None:
        self.rawdata = xmltodict.parse(xml)
        if "ResultListList" in self.rawdata:
            self.events = self.rawdata["ResultListList"].get("ResultList", [])
        elif "EventList" in self.rawdata:
            self.events = self.rawdata["EventList"].get("Event", [])
        else:
            self.events = []
        self.formater()
    
    def formater(self) -> list[Lop]:
        self.data = []
        logger.debug(self.events)
        for i in range(len(self.events)):
            if "Event" in self.events[i]:
                self.events[i] = self.events[i]["Event"]
            
            if "@eventForm" in self.events[i] and self.events[i]["@eventForm"] in ["IndMultiDay", "RelayMultiDay", "RelaySingleDay"]:
                eventorID = self.events[i]["EventId"]
                navn = self.events[i]["Name"]
                startDato = self.events[i]["StartDate"]["Date"]; startDato = date.fromisoformat(startDato)
                sluttDato = self.events[i]["FinishDate"]["Date"]; sluttDato = date.fromisoformat(sluttDato)
                datoer: list[date] = []
                for d in range((sluttDato-startDato).days):
                    datoer.append(startDato + timedelta(days=d+1))

            else:
                eventorID = self.events[i]["EventId"]
                navn = self.events[i]["Name"]
                dato = self.events[i]["EventRace"]["RaceDate"]["Date"]
                datoer = [date.fromisoformat(dato)]
            
            # arr = self.events[i]["Organiser"]["Organisation"]
            # if type(arr) == dict:
            #     arr = arr["Name"]
            # elif type(arr) == list:
            #     arr = ", ".join([i["Name"] for i in arr])
            # try:
            #     lat = self.events[i]["EventRace"]["EventCenterPosition"]["@x"]
            #     lon = self.events[i]["EventRace"]["EventCenterPosition"]["@y"]
            # except Exception as e:
            #     print(e)
            #     lat = 60
            #     lon = 10
            self.data.append(Lop(eventorID, navn, datoer))
        return self.data
    
    def events_valg(self):
        ut = {}
        for lop in self.data:
            for dato in lop.datoer:
                if dato in ut:
                    ut[dato].append(lop)
                else:
                    ut[dato] = [lop]
        return ut
    




    
class EventorAPI:
    def __init__(self) -> None:
        # Lag kontakt med Eventor
        self.headers = {"ApiKey":"1d5a68e8bfb5460ca1dfad5636009ca1"}
        self.base_url = "https://eventor.orientering.no/api"
        self.noe = 1
    
    def get(self, url):
        res = req.get(url, headers=self.headers)
        logger.debug(url)
        if res.status_code != 200:
            return res.status_code
        return Resultat(res.text)
    
    def mineLop(self, startDato, sluttDato):
        url = self.base_url + f"/results/person?fromDate={startDato}&toDate={sluttDato}&personId=3415"
        return self.get(url)
    
    def Lop(self, startDato, sluttDato):
        url = self.base_url + f"/events?fromDate={startDato}&toDate={sluttDato}&classificationIds=1,2,3,4"
        return self.get(url)

