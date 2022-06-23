from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

# from models import election_type,party,constituency,constituency_type,booth_manager,voter,voter_constituency
from . import models

# importing Forms
from .forms import voterAadhar, voterDetails

# BLockchain Imports
from solcx import compile_standard, install_solc
import json
import re

from web3 import Web3
from dotenv import load_dotenv
from web3.middleware import geth_poa_middleware
import os

load_dotenv()

# Create your views here.


def home(request):
    return render(request, "home.html")


def GetVoter(request):
    context = {}
    context["form"] = voterAadhar()
    return render(request, "GetVoter.html", context)


def GetVoterDetails(request):
    # getting Voter Aadhaar Number and Election type from Request
    adhar_no = request.POST.get("aadhar_no")
    election_type = request.POST.get("election_type")

    # Regex Checking for Aadhar Card
    pattern = re.compile("^([0-9]){4}([0-9]){4}([0-9]){4}$")
    pattern.fullmatch(string=adhar_no)

    # Regex match Checking
    if pattern.fullmatch(string=adhar_no):

        # Example populating Data into Django Form
        # data = {'id': game.id, 'position': game.position}
        # form = voterDetails(initial=data)

        try:
            # getting User data From Aadhaar Number from voter model
            obj = models.voter.objects.get(aadhaar_no=adhar_no)

            # getting  voter's counstiuency list
            voter_constituency_id = models.voter_constituency.objects.get(
                voter_id=obj.Id
            )

            # checking If Election Type is valid
            if election_type == "vidhansabha":

                # fetching Voters COnstituency

                print("voter_constituency_id :  ", voter_constituency_id.vidhansabha_id)

                constituency = models.constituency.objects.get(
                    Id=voter_constituency_id.vidhansabha_id
                )
                candidatelist = models.candidate_constituency.objects.filter(
                    constituency_id=constituency.Id, election_type_id=2
                ).values()

                data = {
                    "name": obj.name,
                    "aadhaar_no": obj.aadhaar_no,
                    "age": obj.age,
                    "address": obj.address,
                    "email": obj.email,
                    "phone_no": obj.phone_no,
                    "constituency_name": constituency.name,
                    "constituency_type": "Vidhansabha",
                    "constituency_id": constituency.Id,
                    "voter_id": obj.Id,
                }

                form = voterDetails(initial=data)

                context = {"form": form}
                return render(request, "VoterDetails.html", context)

            elif election_type == "loksabha":
                constituency = models.constituency.objects.get(
                    Id=voter_constituency_id.loksabha_id
                )
                print("constituency_id :  ", constituency.Id, constituency.name)
                candidatelist = models.candidate_constituency.objects.filter(
                    constituency_id=constituency.Id, election_type_id=1
                ).values()

                data = {
                    "name": obj.name,
                    "aadhaar_no": obj.aadhaar_no,
                    "age": obj.age,
                    "address": obj.address,
                    "email": obj.email,
                    "phone_no": obj.phone_no,
                    "constituency_name": constituency.name,
                    "constituency_type": "Loksabha",
                    "constituency_id": constituency.Id,
                    "voter_id": obj.Id,
                }
                form = voterDetails(initial=data)

                context = {"form": form}
                return render(request, "VoterDetails.html", context)

            else:
                return HttpResponse(
                    "Invalid Election Type Please select Proper Election Type"
                )
            context = {"obj": obj}
            return render(request, "VoterDetails.html", context)

        # getting Candidate List In that Consituency For That Election Type

        # fetch form candidate constituenct model by constituency id
        # add list of candidates in dropdown

        except ObjectDoesNotExist as DoesNotExist:
            context = {}
            context["form"] = voterAadhar()
            # return HttpResponse("Hello world")

            return render(request, "GetVoter.html", context)

    else:
        context = {}
        context["form"] = voterAadhar()
        # return HttpResponse("Hello world")
        return render(request, "GetVoter.html", context)


def hello(request):
    return HttpResponse("Hello world")


from django import forms


def voting(request):
    adhar_no = request.POST.get("aadhar_no")
    election_type = request.POST.get("election_type")
    name = request.POST.get("name")
    constituency_name = request.POST.get("constituency_name")
    constituency_type = request.POST.get("constituency_type")
    constituency_id = request.POST.get("constituency_id")
    voter = request.POST.get("voter_id")
    int(constituency_id)
    if constituency_type == "Vidhansabha":
        candidatelist = models.candidate_constituency.objects.filter(
            constituency_id_id=int(constituency_id), election_type_id_id=2
        ).values()
    elif constituency_type == "Loksabha":
        candidatelist = models.candidate_constituency.objects.filter(
            constituency_id_id=int(constituency_id), election_type_id_id=1
        ).values()
        print(type(candidatelist))
        list_of_candi = []
    for candi in candidatelist:
        candidateNames = models.candidate.objects.get(Id=candi["candidate_id_id"])
        list_of_candi.append((candi["candidate_id_id"], str(candidateNames.name)))

    class candidate_List(forms.Form):
        class Meta:
            fields = [
                " candidate",
                "constituency_name",
                "constituency_type",
                "voter_id",
            ]

        candidate = forms.CharField(
            label="Candidate", widget=forms.Select(choices=list_of_candi)
        )
        constituency_name = forms.CharField(label="Constituency", required=True)
        constituency_type = forms.CharField(label="Election Type")
        voter_id = forms.CharField(label="Voter ID", widget=forms.HiddenInput())

    data = {
        " candidatelist": list_of_candi,
        "constituency_name": constituency_name,
        "constituency_type": constituency_type,
        "voter_id": voter,
    }

    form = candidate_List(initial=data)
    context = {"form": form}
    print(list_of_candi)
    return render(request, "Vote.html", context)
    return HttpResponse(candidatelist)


def vote(request):
    return HttpResponse(request)
