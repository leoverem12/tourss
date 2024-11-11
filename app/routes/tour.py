from uuid import uuid4
import random

from flask import Blueprint, render_template, request, redirect, url_for, flash

from app.db import Session, Tour


tour_blueprint = Blueprint("tours", __name__)


@tour_blueprint.get("/")
def index():
    with Session() as session:
        tours = session.query(Tour).where(Tour.is_reserved == False).all()
        random.shuffle(tours)
        return render_template("index.html", tours=tours)


@tour_blueprint.route("/add_tour/", methods=["POST", "GET"])
def add_tour():
    if request.method == "POST":
        with Session() as session:
            number = request.form.get("number")
            name = request.form.get("name")
            img_name_orig = None
            img_name = None
            img_url = "/static/img/default.jpg"

            photo = request.files.get("photo")
            if photo and photo.filename:
                img_name_orig = photo.filename
                img_name = uuid4().hex
                img_url = f"/static/img/{img_name}." + img_name_orig.split(".")[-1]
                photo.save("app" + img_url)

            tour = Tour(
                number=number,
                name=name,
                img_url=img_url,
                img_name=img_name,
                img_name_orig=img_name_orig
            )
            session.add(tour)
            session.commit()
            return redirect(url_for("tours.index"))

    return render_template("add_tour.html")


@tour_blueprint.get("/reserve/<int:id>")
def reserve(id):
    with Session() as session:
        tour = session.query(Tour).where(Tour.id == id).first()
        tour.is_reserved = True
        session.commit()
        return render_template("reserved.html", tour=tour)


@tour_blueprint.get("/manage-tours/")
def manage_tours():
    with Session() as session:
        tours = session.query(Tour).all()
        return render_template("manage_rooms.html", tours=tours)


@tour_blueprint.get("/delete/<int:id>")
def delete_tour(id):
    with Session() as session:
        tour = session.query(Tour).where(Tour.id == id).first()
        session.delete(tour)
        session.commit()
        return redirect(url_for("tours.manage_tours"))


@tour_blueprint.route("/edit-tour/<int:id>", methods=["GET", "POST"])
def edit_tour(id):
    with Session() as session:
        tour = session.query(Tour).where(Tour.id == id).first()
        if request.method == "POST":
            tour.number = request.form.get("number")
            tour.name = request.form.get("name")
            tour.is_reserved = True if request.form.get("is_reserved") else False

            photo = request.files.get("photo")
            if photo and photo.filename:
                tour.img_name_orig = photo.filename
                tour.img_name = uuid4().hex
                tour.img_url = f"/static/img/{tour.img_name}." + tour.img_name_orig.split(".")[-1]
                photo.save("app" + tour.img_url)

            session.commit()
            return redirect(url_for("tours.manage_tours"))

        return render_template("edit_tour.html", tour=tour)