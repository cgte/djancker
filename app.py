import time
import json

from bottle2 import response, request, Bottle


def time_call(fonction):
    """ Cette fonction appele `fonction` mais affiche en plus le temps pris """

    def timed_call(*args, **kwargs):
        t0 = time.time()
        result = fonction(*args, **kwargs)
        print(f"Temps pris par {fonction.__name__} {time.time() - t0:.2f}")
        return result

    return timed_call


class Gift:
    instances = []

    def __init__(self, kind):
        print(f"creating {kind} gift")
        if kind == "small":
            self.weight = 0.5
            self.duration = 1
            self.kind = kind
        elif kind == "medium":
            self.weight = 2
            self.duration = 2
            self.kind = kind
        elif kind == "large":
            self.weight = 5
            self.duration = 3
            self.kind = kind
        else:
            raise ValueError(f"Error kind {kind} is unknown")
        self.instances.append(self)
        self.status = "new"

    @time_call
    def wrap(self):
        print("Starting to wrap")
        time.sleep(self.duration)
        print("Wrapped a %s gift" % self.kind)
        self.status = "wrapped"

    def __str__(self):
        return f"{self.__class__.__name__}: {self.__dict__}"

    def __repr__(self):
        return str(self)


@time_call
def create_gift(kind):
    return Gift(kind)


@time_call
def create_gifts(kinds):
    return [create_gift(kind) for kind in kinds]


@time_call
def onfly_create_gifts(kinds):
    for kind in kinds:
        yield create_gift(kind)


class Sledge:
    def __init__(self):
        self.gifts = []
        self.max_load = 12
        self.time_per_gift = 0.5

    @property
    def free_load(self):
        return self.max_load - sum(gift.weight for gift in self.gifts)

    @property
    def load(self):
        return sum(gift.weight for gift in self.gifts)

    def take_gift(self, gift):
        if gift.weight <= self.free_load:
            self.gifts.append(gift)
            gift.status = "ready"
            return 1
        else:
            return 0
            gift.status = "waiting"

    @time_call
    def ship(self):
        print(f"Shipping {len(self)}")
        print(f"{self.load} kg to be shipped")
        for gift in self:
            gift.status = "shipping"
        for gift in self:
            time.sleep(self.time_per_gift)
            gift.status = "delivered"
        print(f"Shipped  {len(self)}")
        self.gifts = []

    def __len__(self):
        return len(self.gifts)

    def __iter__(self):
        return iter(self.gifts)

    def __getitem__(self, key):
        return self.gifts[key]

    def __contains__(self, gift):
        return gift in self.gifts

    # def __bool__(self):
    #    return bool(self.gifts)
    def __repr__(self):
        return str(self.__dict__)


sledge = Sledge()


# Tiends mais il faudrait qu'on puisse savoir si le cadeau a été pris
# Soit a la valeur de return
#  (exception)


app = Bottle()


@app.route("/create/<kind>")
def create_gift_view(kind):
    try:
        gift = Gift(kind)
    except ValueError as exc:
        yield str(exc)
    gift.wrap()
    sledge.take_gift(gift)
    if gift in sledge:
        yield f"{gift} added to sledge <br/> sledge is now {sledge.gifts}"
        if sledge.free_load == 0:
            message = f"sledge is full, shipping {sledge.gifts}"
            yield message
            sledge.ship()
    else:
        message = f"sledge is full, shipping {sledge.gifts}"
        yield message
        sledge.ship()
        sledge.take_gift(gift)
        message = f"sledge now has {sledge.gifts}"

        yield message


@app.route("/sledge")
def view_sledge():
    response.content_type = "application/json"

    return json.dumps(sledge.__dict__, default=lambda o: o.__dict__)


@app.route("/ship")
def ship():
    if sledge:
        yield f"shipping {sledge.gifts}"
        sledge.ship()
        yield f"shipping done"

    else:
        yield "nothing to do"


@app.get("/gift")
def gift_form():
    return """
        <form action="/gift" method="post">
            Type de cadeau: <input name="kind" type="text" />
            <input value="Ajouter" type="submit" />
        </form>
    """


@app.post("/gift")  # or @route('/login', method='POST')
def process_gift():
    kind = request.forms.get("kind") or request.json.get("kind")
    return create_gift_view(kind)


def process_gifts(gifts):
    for gift in gifts:
        print(gift)
        gift.wrap()
        sledge.take_gift(gift)
        if gift in sledge:
            print(f"current load {sledge.load}")
            continue
        else:
            sledge.ship()
            sledge.take_gift(gift)
            print(f"!!! test getitem : {sledge[0]}")
            if gift not in sledge:
                print("Error, sledge should take the gift after shipping")
    if sledge:
        print("Last delivery")
        sledge.ship()


@app.get("/gifts")
def gifts():
    yield """
    <script language="javascript">
setInterval(function(){
   window.location.reload(1);
}, 500);
</script>
    """
    yield "<ul>"
    for gift in Gift.instances:
        yield f"<li>{gift}</li>"
    yield "</ul>"


def create_and_process(gift_types):
    process_gifts(onfly_create_gifts(gift_types))


from wsgiref.simple_server import make_server, WSGIServer
from socketserver import ThreadingMixIn


class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):
    pass


if __name__ == "__main__":
    import sys

    httpd = make_server("", sys.argv[2], app, ThreadingWSGIServer)
    try:
        httpd.serve_forever()
    except:
        httpd.shutdown()
        httpd.server_close()
        # app.run(host="localhost", port=8080, debug=True)
