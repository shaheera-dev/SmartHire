
import os
from flask import Flask, render_template,request,redirect,url_for, session, flash
from database import create_table, add_application,get_applications,get_dashboard_stats,update_application,delete_application,get_application_by_id,add_user_id_column, create_settings_table, get_user_settings, update_user_settings, create_notifications_table, add_notification, get_notifications, get_unread_notification_count, mark_notification_read, delete_notification, create_database_indexes
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

from database import (
    create_table,
    add_user_id_column,
    add_application,
    get_applications,
    get_dashboard_stats,
    update_application,
    delete_application,
    get_application_by_id,
    create_user,
    get_user_by_email,
    get_user_by_id,
    update_user_profile,
    update_user_password,
    add_interview,
    get_interviews,
    get_interview_by_id,
    update_interview,
    delete_interview
)
from functools import wraps
app = Flask(__name__)
@app.context_processor
def inject_notification_count():
    if 'user_id' in session:
        count = get_unread_notification_count(session['user_id'])
    else:
        count = 0

    return dict(unread_count=count)

# app.secret_key = 'smarthire-development-secret-key'

import os

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "smarthire-local-development-key"
)

def login_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return route_function(*args, **kwargs)

    return wrapper

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if get_user_by_email(email):
            return render_template(
                'register.html',
                error='Email already registered!'
            )

        hashed_password = generate_password_hash(password)

        create_user(username, email, hashed_password)

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = get_user_by_email(email)

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']

            return redirect(url_for('home'))

        return render_template(
            'login.html',
            error='Invalid email or password!'
        )

    return render_template('login.html')
# @app.route('/')
# @login_required
# def home():

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# @app.route('/')
# @login_required
# def home():
#     user_id = session['user_id']


#     applications=get_applications(user_id)
#     stats=get_dashboard_stats(user_id)
#     return render_template('index.html',applications=applications,stats=stats)

@app.route('/')
@login_required
def home():
    user_id = session['user_id']

    applications = get_applications(user_id)
    stats = get_dashboard_stats(user_id)
    unread_count = get_unread_notification_count(user_id)

    return render_template(
        'index.html',
        applications=applications,
        stats=stats,
        unread_count=unread_count
    )

@app.route('/my-applications')
@login_required
def my_applications():
    user_id = session['user_id']
    applications = get_applications(user_id)

    return render_template(
        'my_applications.html',
        applications=applications
    )


@app.route('/application/<int:app_id>')
@login_required
def application_details(app_id):
    application = get_application_by_id(
        app_id,
        session['user_id']
    )

    if application is None:
        return "Application not found", 404

    return render_template(
        'application_details.html',
        application=application
    )

# @app.route('/add-job')
@app.route('/add-job', methods=['GET', 'POST'])
@login_required
def add_job():

    if request.method == 'POST':

        company = request.form['company']
        position = request.form['position']
        location = request.form['location']
        salary = request.form['salary']
        date = request.form['application_date']
        status = request.form['status']
        description = request.form['description']

        add_application(
            session['user_id'],company, position, location, salary,
            date, status, description
        )

        add_notification(
    session['user_id'],
    'New Application Added',
    f'You added {position} at {company}.',
    'application'
)

        return render_template('add_job.html', success=True)
    return render_template('add_job.html')

# @app.route('/edit-job/<int:app_id>', methods=['GET', 'POST'])
# @login_required
# def edit_job(app_id):

#     if request.method == 'POST':
#         update_application(
#             app_id,
#             session['user_id'],
#             request.form['company'],
#             request.form['position'],
#             request.form['location'],
#             request.form['salary'],
#             request.form['application_date'],
#             request.form['status'],
#             request.form['description']
#         )

#         return redirect(url_for('home'))

#     application = get_application_by_id(app_id, session['user_id'])

#     if application is None:
#         return "Application not found", 404

#     return render_template('edit_job.html', application=application)


@app.route('/edit-job/<int:app_id>', methods=['GET', 'POST'])
@login_required
def edit_job(app_id):

    user_id = session['user_id']

    application = get_application_by_id(app_id, user_id)

    if application is None:
        return "Application not found", 404

    if request.method == 'POST':

        old_status = application['status']
        new_status = request.form['status']

        update_application(
            app_id,
            user_id,
            request.form['company'],
            request.form['position'],
            request.form['location'],
            request.form['salary'],
            request.form['application_date'],
            new_status,
            request.form['description']
        )

        if old_status.strip().lower() != new_status.strip().lower():

            add_notification(
                user_id,
                'Application Status Updated',
                f'{application["company"]}: Status changed from {old_status} to {new_status}.',
                'application'
            )

        return redirect(url_for('home'))

    return render_template(
        'edit_job.html',
        application=application
    )



@app.route('/delete-job/<int:app_id>', methods=['POST'])
@login_required
def delete_job(app_id):
    delete_application(app_id, session['user_id'])
    return redirect(url_for('home'))


# Interview Tracker

@app.route('/interviews')
@login_required
def interviews():
    user_id = session['user_id']

    interview_list = get_interviews(user_id)

    return render_template(
        'interviews.html',
        interviews=interview_list
    )


@app.route('/interviews/add', methods=['GET', 'POST'])
@login_required
def schedule_interview():

    user_id = session['user_id']

    if request.method == 'POST':

        # add_interview(
        #     user_id,
        #     request.form['application_id'],
        #     request.form['interview_date'],
        #     request.form['interview_time'],
        #     request.form['interview_type'],
        #     request.form['interview_round'],
        #     request.form['interviewer'],
        #     request.form['meeting_link'],
        #     request.form['status'],
        #     request.form['notes']
        # )
        application_id = request.form['application_id']

        application = get_application_by_id(
        application_id,
        user_id
        )

        if application is None:
           return "Application not found", 404

        interview_date = request.form['interview_date']
        interview_time = request.form['interview_time']

        add_interview(
            user_id,
            application_id,
            interview_date,
            interview_time,
            request.form['interview_type'],
            request.form['interview_round'],
            request.form['interviewer'],
            request.form['meeting_link'],
            request.form['status'],
            request.form['notes']
        )

        add_notification(
            
            user_id,
            'Interview Scheduled',
            f'Interview for {application["position"]} at {application["company"]} scheduled on {interview_date} at {interview_time}.',
            'interview'
        )

        return redirect(url_for('interviews'))

    applications = get_applications(user_id)

    return render_template(
            'add_interview.html',
            applications=applications
            )


@app.route('/interviews/edit/<int:interview_id>',
           methods=['GET', 'POST'])
@login_required
def edit_interview(interview_id):

    user_id = session['user_id']

    interview = get_interview_by_id(interview_id, user_id)

    if interview is None:
        return "Interview not found", 404

    if request.method == 'POST':

        update_interview(
            interview_id,
            user_id,
            request.form['application_id'],
            request.form['interview_date'],
            request.form['interview_time'],
            request.form['interview_type'],
            request.form['interview_round'],
            request.form['interviewer'],
            request.form['meeting_link'],
            request.form['status'],
            request.form['notes']
        )
    new_date = request.form['interview_date']
    new_time = request.form['interview_time']

    if (
        interview['interview_date'] != new_date
        or (interview['interview_time'] or '') != new_time
    ):

        add_notification(
        user_id,
        'Interview Rescheduled',
        f'Interview for {interview["company"]} has been rescheduled to {new_date} at {new_time}.',
        'interview'
    )

        return redirect(url_for('interviews'))

    applications = get_applications(user_id)

    return render_template(
        'edit_interview.html',
        interview=interview,
        applications=applications
    )


@app.route('/interviews/delete/<int:interview_id>',
           methods=['POST'])
@login_required
def remove_interview(interview_id):

    delete_interview(interview_id, session['user_id'])

    return redirect(url_for('interviews'))  



# MY PROFILE

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():

    user_id = session['user_id']

    if request.method == 'POST':

        username = request.form['username'].strip()
        email = request.form['email'].strip()

        if not username or not email:
            flash('Username and email are required.', 'error')
        else:
            updated = update_user_profile(
                user_id, username, email
            )

            if updated:
                session['username'] = username
                flash('Profile updated successfully!', 'success')
            else:
                flash('This email is already registered.', 'error')

        return redirect(url_for('profile'))

    user = get_user_by_id(user_id)

    return render_template('profile.html', user=user)


# CHANGE PASSWORD

@app.route('/change-password', methods=['POST'])
@login_required
def change_password():

    user_id = session['user_id']

    user = get_user_by_id(user_id)

    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    if not check_password_hash(user['password'], current_password):
        flash('Current password is incorrect.', 'error')

    elif len(new_password) < 8:
        flash('New password must contain at least 8 characters.', 'error')

    elif new_password != confirm_password:
        flash('New passwords do not match.', 'error')

    else:
        hashed_password = generate_password_hash(new_password)

        update_user_password(user_id, hashed_password)

        flash('Password changed successfully!', 'success')

    return redirect(url_for('profile'))


# SETTINGS PAGE
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():

    user_id = session['user_id']

    if request.method == 'POST':

        email_notifications = (
            1 if request.form.get('email_notifications') == 'on' else 0
        )

        interview_reminders = (
            1 if request.form.get('interview_reminders') == 'on' else 0
        )

        application_updates = (
            1 if request.form.get('application_updates') == 'on' else 0
        )

        update_user_settings(
            user_id,
            email_notifications,
            interview_reminders,
            application_updates
        )

        flash('Settings saved successfully!', 'success')

        return redirect(url_for('settings'))

    user_settings = get_user_settings(user_id)

    return render_template(
        'settings.html',
        settings=user_settings
    )


@app.route('/notifications')
@login_required
def notifications():
    user_id = session['user_id']

    all_notifications = get_notifications(user_id)
    unread_count = get_unread_notification_count(user_id)

    return render_template(
        'notifications.html',
        notifications=all_notifications,
        unread_count=unread_count
    )


@app.route('/notifications/read/<int:notification_id>', methods=['POST'])
@login_required
def read_notification(notification_id):
    user_id = session['user_id']

    mark_notification_read(notification_id, user_id)

    flash('Notification marked as read.', 'success')
    return redirect(url_for('notifications'))


@app.route('/notifications/delete/<int:notification_id>', methods=['POST'])
@login_required
def remove_notification(notification_id):
    user_id = session['user_id']

    delete_notification(notification_id, user_id)

    flash('Notification deleted successfully.', 'success')
    return redirect(url_for('notifications'))


@app.route('/notifications/read-all', methods=['POST'])
@login_required
def read_all_notifications():
    user_id = session['user_id']

    all_notifications = get_notifications(user_id)

    for notification in all_notifications:
        if not notification['is_read']:
            mark_notification_read(notification['id'], user_id)

    flash('All notifications marked as read.', 'success')
    return redirect(url_for('notifications'))



create_table()
add_user_id_column()
create_settings_table()
create_notifications_table()
create_database_indexes()

if __name__ == '__main__':
    app.run(debug=False)