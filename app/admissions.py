from flask import render_template, redirect, url_for, flash, request
from models import *
from datetime import datetime
from collections import Counter
import plotly.express as px


def view_admissions(app):
    @app.route('/view_admissions')
    def view_admissions():
        admissions = Admission.query.all()
        return render_template('view_admissions.html', admissions=admissions)


def add_admission(app):
    @app.route('/add_admission', methods=['GET', 'POST'])
    def add_admission():
        if request.method == 'POST':
            patient_id = request.form['patient_id']
            admission_date = request.form['admission_date']
            discharge_date = request.form['discharge_date']
            reason_for_admission = request.form['reason_for_admission']
            admitted_by = request.form['admitted_by']

            admission_date = datetime.strptime(admission_date, "%Y-%m-%dT%H:%M")
            if discharge_date:
                discharge_date = datetime.strptime(discharge_date, "%Y-%m-%dT%H:%M")
            else:
                discharge_date = None

            admission = Admission(
                patient_id=patient_id,
                admission_date=admission_date,
                discharge_date=discharge_date,
                reason_for_admission=reason_for_admission,
                admitted_by=admitted_by
            )

            try:
                db.session.add(admission)
                db.session.commit()
                flash('Поступление успешно добавлено!', 'success')
            except Exception as e:
                db.session.rollback()
                flash('Произошла ошибка при добавлении поступления. Попробуйте снова.', 'danger')

            return redirect(url_for('add_admission'))

        patients = Patient.query.all()
        doctors = Doctor.query.all()

        return render_template('add_admission.html', patients=patients, doctors=doctors)


def edit_admission(app):
    @app.route('/edit_admission/<int:admission_id>', methods=['GET', 'POST'])
    def edit_admission(admission_id):
        admission = Admission.query.get_or_404(admission_id)
        patients = Patient.query.all()
        doctors = Doctor.query.all()

        if request.method == 'POST':
            admission.patient_id = request.form['patient_id']
            admission.admission_date = request.form['admission_date']
            admission.discharge_date = request.form['discharge_date']
            admission.reason_for_admission = request.form['reason_for_admission']
            admission.admitted_by = request.form['admitted_by']

            admission.admission_date = datetime.strptime(admission.admission_date, "%Y-%m-%dT%H:%M")
            if admission.discharge_date:
                admission.discharge_date = datetime.strptime(admission.discharge_date, "%Y-%m-%dT%H:%M")
            else:
                admission.discharge_date = None

            try:
                db.session.commit()
                flash('Поступление успешно обновлено!', 'success')
            except Exception as e:
                db.session.rollback()
                flash('Произошла ошибка при обновлении поступления. Попробуйте снова.', 'danger')

            return redirect(url_for('view_admissions'))

        return render_template('edit_admission.html', patients=patients, doctors=doctors, admission=admission)


def delete_admission(app):
    @app.route('/delete_admission/<int:admission_id>', methods=['POST'])
    def delete_admission(admission_id):
        admission = Admission.query.get_or_404(admission_id)
        try:
            db.session.delete(admission)
            db.session.commit()
            flash("Admission deleted successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")
        return redirect(url_for('view_admissions'))


def analyze_admissions(app):
    @app.route('/analyze_admissions')
    def analyze_admissions():
        admissions = Admission.query.all()

        # Analyze data
        admission_dates = [admission.admission_date.date() for admission in admissions]
        reasons = [admission.reason_for_admission for admission in admissions]
        doctors = [admission.admitted_by for admission in admissions]
        admission_hours = [admission.admission_date.hour for admission in admissions]
        lengths_of_stay = [(admission.discharge_date - admission.admission_date).days if admission.discharge_date else 0 for admission in admissions]
        patient_ages = [(datetime.now().date() - admission.patient.birth_date).days // 365 for admission in admissions]
        patient_genders = [admission.patient.gender for admission in admissions]

        # Count admissions per day
        admission_counts = Counter(admission_dates)
        admission_dates = list(admission_counts.keys())
        admission_counts = list(admission_counts.values())

        reason_counts = Counter(reasons)
        reasons = list(reason_counts.keys())
        reason_counts = list(reason_counts.values())

        doctor_counts = Counter(doctors)
        doctors = list(doctor_counts.keys())
        doctor_counts = list(doctor_counts.values())

        hour_counts = Counter(admission_hours)
        hours = list(hour_counts.keys())
        hour_counts = list(hour_counts.values())

        age_groups = ['0-10', '11-20', '21-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81+']
        age_counts = Counter([age_groups[min(patient_age // 10, 8)] for patient_age in patient_ages])
        age_groups = list(age_counts.keys())
        age_counts = list(age_counts.values())

        gender_counts = Counter(patient_genders)
        genders = list(gender_counts.keys())
        gender_counts = list(gender_counts.values())

        fig1 = px.bar(x=admission_dates, y=admission_counts, labels={'x': 'Date', 'y': 'Number of Admissions'},
                      title='Admissions per Day')
        fig2 = px.pie(names=reasons, values=reason_counts, title='Reasons for Admission')
        fig3 = px.bar(x=doctors, y=doctor_counts, labels={'x': 'Doctor', 'y': 'Number of Admissions'},
                      title='Admissions per Doctor')
        fig4 = px.bar(x=hours, y=hour_counts, labels={'x': 'Hour', 'y': 'Number of Admissions'},
                      title='Admissions by Time of Day')
        fig5 = px.line(x=list(range(len(lengths_of_stay))), y=lengths_of_stay,
                       labels={'x': 'Admission', 'y': 'Length of Stay (days)'}, title='Average Length of Stay')
        fig6 = px.bar(x=age_groups, y=age_counts, labels={'x': 'Age Group', 'y': 'Number of Admissions'},
                      title='Admissions by Age Group')
        fig7 = px.pie(names=genders, values=gender_counts, title='Admissions by Gender')

        graph1_html = fig1.to_html(full_html=False)
        graph2_html = fig2.to_html(full_html=False)
        graph3_html = fig3.to_html(full_html=False)
        graph4_html = fig4.to_html(full_html=False)
        graph5_html = fig5.to_html(full_html=False)
        graph6_html = fig6.to_html(full_html=False)
        graph7_html = fig7.to_html(full_html=False)

        return render_template('analyze_admissions.html', graph1=graph1_html, graph2=graph2_html,
                               graph3=graph3_html, graph4=graph4_html, graph5=graph5_html, graph6=graph6_html,
                               graph7=graph7_html)
