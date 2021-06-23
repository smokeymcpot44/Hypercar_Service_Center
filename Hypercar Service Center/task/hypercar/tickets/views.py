from django.views import View
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from collections import deque


class WelcomeView(View):
    def get(self, request, *args, **kwargs):
        welcome_heading = "<h2>Welcome to the Hypercar Service!</h2>"
        return HttpResponse(welcome_heading)


class MenuView(View):
    menu = {
        "change_oil": "Change oil",
        "inflate_tires": "Inflate tires",
        "diagnostic": "Get diagnostic test",
    }

    def get(self, request, *args, **kwargs):
        return render(request, 'tickets/index.html', context={'menu': self.menu})


line_of_cars = {'change_oil': deque(), 'inflate_tires': deque(), "diagnostic": deque()}
ticket_number = 0


class GetTicketView(View):

    global line_of_cars

    def get(self, request, service_name, *args, **kwargs):
        global ticket_number
        ticket_number += 1
        ticket_wait_time = self.count_time(service_name)
        line_of_cars[service_name].appendleft(ticket_number)
        ticket_res = f"<div>Your number is {ticket_number}</div>"
        wait_res = f"<div>Please wait around {ticket_wait_time} minutes</div>"
        return HttpResponse(ticket_res + wait_res)

    def count_time(self, service):
        wait_time = 0
        if service == "change_oil":
            wait_time = len(line_of_cars[service]) * 2
        elif service == "inflate_tires":
            wait_time = len(line_of_cars[service]) * 5 + len(line_of_cars['change_oil']) * 2
        elif service == "diagnostic":
            wait_time = len(line_of_cars['inflate_tires']) * 5 + len(line_of_cars['change_oil']) * 2 + len(line_of_cars[service]) * 30
        return wait_time


last_customer = 0


class OperatorView(View):
    def get(self, request):
        return render(request, 'operator/menu.html', context = {'cars': line_of_cars})

    def post(self, request, *args, **kwargs):
        global line_of_cars
        global last_customer
        service_queue = deque()
        if len(line_of_cars['change_oil']) > 0:
            service_queue.appendleft(line_of_cars['change_oil'].pop())
        elif len(line_of_cars['inflate_tires']) > 0:
            service_queue.appendleft(line_of_cars['inflate_tires'].pop())
        elif len(line_of_cars['diagnostic']) > 0:
            service_queue.appendleft(line_of_cars['diagnostic'].pop())
        else:
            pass
        last_customer = service_queue.pop()
        return redirect("/next")


class NextView(View):
    def get(self, request, *args, **kwargs):
        if last_customer:
            return HttpResponse(f"<div>Next ticket #{last_customer}</div>")
        else:
            return HttpResponse(f"<div>Waiting for the next client</div>")
