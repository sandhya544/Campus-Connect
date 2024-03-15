import random
import string
from django.utils import timezone
from datetime import datetime
from .models import Student, skill, certification, internship, project, Event
from django.contrib.auth import authenticate, logout, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import skill, certification, internship, project, Student, Event
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from django.db.models import Q
import csv


def index(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('home')
    if request.method == "POST":
        event_code = request.POST.get('eventCode')
        print(event_code)
        if Event.objects.filter(eventCode=event_code).exists():
            event = Event.objects.get(eventCode=event_code)
            today = timezone.now().date()
            if event.expiryDate is not None:
                if event.expiryDate.date() < today:
                    messages.error(request, 'Event Code Expired')
                    return redirect('index')
                if event.date.date() > today:
                    messages.error(request, 'Event is not started yet')
                    return redirect('index')
            if request.user.is_authenticated and not request.user.is_superuser:
                if event.profiles.filter(rollNumber=request.user).exists():
                    messages.error(request, 'students are not allowed to view this page')
                    return redirect('login')
            return redirect('showEvent', event_code=event_code)
        else:
            messages.error(request, 'Event does not exist')
            return redirect('index')
    return render(request, 'index.html')


def admin_login(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('home')
    if request.method == "POST":
        username = request.POST["user_name"]
        password = request.POST["pass_word"]
        user = authenticate(request, username=username, password=password, is_active=True)
        if user is not None:

            if user.is_active:
                if user.is_superuser:
                    login(request, user)
                    messages.success(request, 'Login Successful')
                    return redirect('home')
                else:
                    messages.error(request, 'You are not authorized to view this page')
                    return redirect('index')
            else:
                messages.error(request, 'User is not verified')
                return redirect('login')
        else:
            messages.error(request, 'Invalid Credentials or User is not verified')
            return redirect('login')
    return render(request, 'admin_login.html')


def signup(request):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        username = request.POST["rollNumber"].lower()
        email = username + '@svrec.ac.in'
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        if not first_name or not last_name or not username or not email or not password or not confirm_password:
            messages.error(request, 'All fields are required')
            return redirect('register')
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('register')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username or email already exists')
            return redirect('register')
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            is_active=False
        )
        # verification code
        user.save()
        st = Student.objects.create(rollNumber=user, status=False)
        st.save()
        code = ''.join(random.choices(string.digits, k=6))
        send_mail('OTP Code From Team CDC',
                  'Welcome to SVREC Career Portal CAMPUS-CONNECT,  ' + code + ' is your verification code for Signup',
                  settings.EMAIL_HOST_USER,
                  [email], fail_silently=False)
        messages.success(request, 'Account created successfully, Please verify your email')
        request.session['otp'] = code
        return redirect('verify', username=username)
    else:
        return render(request, 'register.html')


def check(request):
    if request.method == "POST":
        rollNumber = request.POST['rollNumber']
        rollNumber = rollNumber.lower()
        if User.objects.filter(username=rollNumber).exists():
            if User.objects.get(username=rollNumber).is_active:
                messages.error(request, 'User is already verified')
                return redirect('login')
            else:
                code = ''.join(random.choices(string.digits, k=6))
                send_mail('OTP Code From Team CDC',
                          'Welcome to SVREC Career Portal CAMPUS-CONNECT,  ' + code + ' is your verification code for Signup',
                          settings.EMAIL_HOST_USER,
                          [User.objects.get(username=rollNumber).email], fail_silently=False)
                messages.success(request, 'OTP sent successfully')
                request.session['otp'] = code
                return redirect('verify', username=rollNumber)
        else:
            messages.error(request, 'User does not exist, Please register')
            return redirect('register')
    else:
        return render(request, 'check.html')


def verify(request, username):
    if User.objects.get(username=username).is_active:
        messages.error(request, 'User is already verified')
        return redirect('login')
    else:
        if request.method == "POST":
            code = request.session['otp']
            code1 = request.POST['otp']
            if code1 == code:
                user = User.objects.get(username=username)
                user.is_active = True
                user.save()
                messages.success(request, 'Account verified successfully, You can login now')
                return redirect('login')
            else:
                messages.error(request, 'Invalid verification code')
                return redirect('verify', username=username)
        else:
            return render(request, 'verify.html')


def loginView(request):
    if request.method == 'POST':
        username = request.POST.get('rollNumber').lower()
        password = request.POST['passWord']
        user = authenticate(request, username=username, password=password, is_active=True)
        # print(user.first_name)
        if user is not None:
            login(request, user)
            if user.is_active:
                if user.is_superuser:
                    messages.success(request, 'Login Successful')
                    return redirect('home')
                else:
                    messages.success(request, 'Login Successful')
                    return redirect('profile')
            else:
                messages.error(request, 'User is not verified')
                return redirect('login')
        else:
            messages.error(request, 'Invalid Credentials or User is not verified')
            return redirect('login')
    if request.user.is_authenticated:
        if request.user.is_superuser:
            messages.error(request, 'You are already logged in')
            return redirect('home')
        else:
            messages.warning(request, 'You are already logged in')
            return redirect('profile')
    else:
        return render(request, 'login.html')


def profile(request):
    # print(request.user.last_name)
    if request.user.is_authenticated:
        student_data = Student.objects.get(rollNumber=request.user)
        if 'about-btn' in request.POST:
            tagline = request.POST['tagLine']
            about = request.POST['about']
            gender = int(request.POST['gender'])
            st = Student.objects.get(rollNumber=request.user)
            st.tagline = tagline
            st.about = about
            st.gender = gender
            st.status = False
            st.save()
            print(request.user)
            messages.success(request, 'About updated Successfully')
            redirect('profile')
        elif 'edu-btn' in request.POST:
            gradCollege = request.POST['gradCollege']
            gradBranch = request.POST['gradBranch']
            gradPercentage = request.POST['gradPercentage']
            gradYear = request.POST['gradYear']
            pucCollege = request.POST['pucCollege']
            pucBranch = request.POST['pucBranch']
            pucPercentage = request.POST['pucPercentage']
            pucYear = request.POST['pucYear']
            school = request.POST['sscName']
            sscBranch = request.POST['sscBranch']
            sscPercentage = request.POST['sscPercentage']
            sscYear = request.POST['sscYear']

            st = Student.objects.get(rollNumber=request.user)
            st.GradCollege = gradCollege
            st.GradBranch = gradBranch
            st.GradPercentage = gradPercentage
            st.GradYear = gradYear
            st.PucCollege = pucCollege
            st.PucBranch = pucBranch
            st.PucPercentage = pucPercentage
            st.PucYear = pucYear
            st.SscCollege = school
            st.SscBranch = sscBranch
            st.SscPercentage = sscPercentage
            st.SscYear = sscYear
            st.status = False
            st.save()
            print('Done')
            messages.success(request, 'Education Fields updated Successfully')
            redirect('profile')
        elif 'skill-btn' in request.POST:
            skillName = request.POST['skillName']
            proficiency = int(request.POST['proficiency'])
            print(proficiency)
            st = Student.objects.get(rollNumber=request.user)
            # if skill already in skills model raise message
            if skill.objects.filter(skillName=skillName).exists():
                sk = skill.objects.get(skillName=skillName)
                st.skills.add(sk)
                st.status = False
                st.save()
                messages.success(request, 'Skill Added Successfully')
                redirect('profile')
            else:
                sk = skill.objects.create(skillName=skillName, proficiency=proficiency)
                sk.save()
                st.skills.add(sk)
                st.status = False
                st.save()
                messages.success(request, 'Skill Added Successfully')
                redirect('profile')
        elif 'cert-btn' in request.POST:
            certName = request.POST['certName']
            certYear = request.POST['certYear']
            certUrl = request.POST['certURL']
            st = Student.objects.get(rollNumber=request.user)
            if certification.objects.filter(certificationName=certName, rollNumber=request.user).exists():
                messages.error(request, 'Certification already exists')
                redirect('profile')
            else:
                cert = certification.objects.create(rollNumber=request.user, certificationName=certName, year=certYear,
                                                    url=certUrl)
                cert.save()
                st.certifications.add(cert)
                st.status = False
                st.save()
                messages.success(request, 'Certification Added Successfully')
                redirect('profile')
        elif 'intern-btn' in request.POST:
            internName = request.POST['iName']
            internYear = request.POST['iYear']
            internDuration = request.POST['iDuration']
            internProvider = request.POST['iProvider']
            iStatus = request.POST['iStatus']
            internUrl = request.POST['iUrl']
            st = Student.objects.get(rollNumber=request.user)
            if internship.objects.filter(internshipName=internName, rollNumber=request.user).exists():
                if st.certifications.filter(certificationName=internName).exists():
                    messages.error(request, 'Internship already exists')
                    redirect('profile')
                else:
                    intern = internship.objects.create(rollNumber=request.user, internshipName=internName,
                                                       year=internYear,
                                                       duration=internDuration, provider=internProvider,
                                                       status=iStatus, url=internUrl)
                    intern.save()
                    st.internships.add(intern)
                    st.status = False
                    st.save()
                    messages.success(request, 'Internship Added Successfully')
                    redirect('profile')
            else:
                intern = internship.objects.create(rollNumber=request.user, internshipName=internName, year=internYear,
                                                   duration=internDuration, provider=internProvider,
                                                   status=iStatus, url=internUrl)
                intern.save()
                st.internships.add(intern)
                st.status = False
                st.save()
                messages.success(request, 'Internship Added Successfully')
                print('Done')
                redirect('profile')
        elif 'project-btn' in request.POST:
            projectName = request.POST['pName']
            projectDescription = request.POST['pDescription']
            projectYear = request.POST['pYear']
            projectUrl = request.POST['pURL']
            st = Student.objects.get(rollNumber=request.user)
            if project.objects.filter(projectName=projectName, rollNumber=request.user).exists():
                if st.projects.filter(projectName=projectName).exists():
                    messages.error(request, 'Project already exists')
                    redirect('profile')
                else:
                    proj = project.objects.create(rollNumber=request.user, projectName=projectName,
                                                  description=projectDescription, year=projectYear,
                                                  githubUrl=projectUrl)
                    proj.save()
                    st.projects.add(proj)
                    st.status = False
                    st.save()
                    messages.success(request, 'Project Added Successfully')
                    redirect('profile')
            else:
                proj = project.objects.create(rollNumber=request.user, projectName=projectName,
                                              description=projectDescription, year=projectYear, githubUrl=projectUrl)
                proj.save()
                st.projects.add(proj)
                st.status = False
                st.save()
                messages.success(request, 'Project Added Successfully')
                redirect('profile')
        elif 'contact-btn' in request.POST:
            address = request.POST['address']
            gProfile = request.POST['gProfile']
            linkedin = request.POST['linkedin']
            st = Student.objects.get(rollNumber=request.user)
            st.address = address
            st.githubProfile = gProfile
            st.linkedinProfile = linkedin
            st.status = False
            st.save()
            messages.success(request, 'Contact Details Updated Successfully')
            redirect('profile')

        return render(request, 'profile.html', {'student_data': student_data})

    else:
        messages.error(request, 'You are not authorized to view this page')
        return redirect('login')


@login_required(login_url='login')
def dashboard(request):
    events = Event.objects.all().order_by('-date').reverse()
    if request.user.is_superuser:
        if request.method == 'POST':
            if 'create-btn' in request.POST:
                eventName = request.POST['eventName']
                #eventName = request.POST.get('eventName')
                company = request.POST['company']
                eventDescription = request.POST['eventDescription']
                eventDate = request.POST['eventDate']
                print(eventDate)
                eventID = request.POST.get('eventID')
                email = request.POST['email']
                expiryDate = request.POST['expiryDate']
                print(expiryDate)
                # eventTime = request.POST['eventTime']
                eventVenue = request.POST['eventVenue']
                eventCode = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
                event = Event.objects.create(title=eventName, company=company, description=eventDescription,
                                             date=eventDate, expiryDate=expiryDate, eventId=eventID, email=email,
                                             venue=eventVenue, eventCode=eventCode)
                event.save()
                messages.success(request, 'Event Created Successfully')
                return redirect('home')
            elif 'search-btn' in request.POST:
                search = request.POST['search']
                events = Event.objects.filter(company__icontains=search)
                return render(request, 'dashboard.html', {'events': events
                                                          })
        else:
            return render(request, 'dashboard.html', {'events': events})
    else:
        messages.error(request, 'You are not authorized to view this page')
        return redirect('index')


@login_required(login_url='login')
def logoutV(request):
    logout(request)
    messages.success(request, 'Logout Successful')
    return redirect('index')


def addStudent(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            rollNumber = request.POST['rollNumber']
            rollNumber = rollNumber.lower()
            firstName = request.POST['firstName']
            lastName = request.POST['lastName']
            email = rollNumber + '@svrec.ac.in'
            password = request.POST['passWord']
            confirmPassword = request.POST['confirmPassWord']
            if password != confirmPassword and len(password) < 8:
                messages.error(request, 'Password and Confirm Password should be same and minimum 8 characters')
                return redirect('addStudent')
            else:
                if User.objects.filter(username=rollNumber).exists():
                    messages.error(request, 'User already exists')
                    return redirect('addStudent')
                else:
                    user = User.objects.create_user(username=rollNumber, password=password, email=email,
                                                    first_name=firstName,
                                                    last_name=lastName, is_active=True)
                    user.save()
                    roll = User.objects.get(username=rollNumber)
                    st = Student.objects.create(rollNumber=roll, status=False)
                    st.save()

                    student_mail = rollNumber + "@svrec.ac.in"
                    subject = 'Welcome to SVREC Career Portal CAMPUS-CONNECT'
                    message = 'Your account is created by admin, Please login with your <b>roll number</b> and <b>password: ' + password + '</b> and update your profile'
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = [student_mail]
                    send_mail(subject, message, email_from, recipient_list)

                    messages.success(request, 'Student Added Successfully')
                    return redirect('addStudent')
        else:
            return render(request, 'addStudent.html')
    else:
        messages.error(request, 'You are not authorized to view this page')
        return redirect('index')


def preview(request):
    if request.user.is_authenticated:  # request.user.is_superuser
        student_data = Student.objects.get(rollNumber=request.user)
        return render(request, 'preview.html', {'student_data': student_data})
    else:
        messages.error(request, 'You are not authorized to view this page')
        return redirect('login')


def deleteSkill(request, id):
    if request.user.is_authenticated:
        st = Student.objects.get(rollNumber=request.user)
        sk = skill.objects.get(id=id)
        st.skills.remove(sk)
        st.save()
        messages.success(request, 'Skill Deleted Successfully')
        return redirect('profile')
    else:
        messages.error(request, 'You are not authorized to view this page')
        return redirect('login')


def deleteCertification(request, id):
    if request.user.is_authenticated:
        st = Student.objects.get(rollNumber=request.user)
        cert = certification.objects.get(id=id)
        st.certifications.remove(cert)
        st.save()
        messages.success(request, 'Certification Deleted Successfully')
        return redirect('profile')
    else:
        messages.error(request, 'You are not authorized to view this page')
        return redirect('login')


def deleteInternship(request, id):
    if request.user.is_authenticated:
        st = Student.objects.get(rollNumber=request.user)
        intern = internship.objects.get(id=id)
        st.internships.remove(intern)
        st.save()
        messages.success(request, 'Internship Deleted Successfully')
        return redirect('profile')
    else:
        messages.error(request, 'You are not authorized to view this page')
        return redirect('login')


def deleteProject(request, id):
    if request.user.is_authenticated:
        st = Student.objects.get(rollNumber=request.user)
        proj = project.objects.get(id=id)
        st.projects.remove(proj)
        st.save()
        messages.success(request, 'Project Deleted Successfully')
        return redirect('profile')
    else:
        messages.error(request, 'You are not authorized to view this page')
        return redirect('login')


def updateEvent(request, id):
    if request.user.is_superuser:
        event = Event.objects.get(id=id)
        if event is None:
            messages.error(request, 'Event does not exist')
            return redirect('home')
        else:
            if request.method == 'POST':
                eventName = request.POST['eventName']
                company = request.POST.get('company')
                eventDescription = request.POST['eventDescription']
                eventDate = request.POST['eventDate']
                expiryDate = request.POST['expiryDate']
                eventVenue = request.POST['eventVenue']
                event_id = request.POST.get('eventID')
                email = request.POST['email']
                event.title = eventName
                event.description = eventDescription
                event.date = eventDate
                event.expiryDate = expiryDate
                event.venue = eventVenue
                event.eventId = event_id
                event.email = email
                event.save()
                messages.success(request, 'Event Updated Successfully')
                return redirect('home')
            else:
                return render(request, 'update.html', {'event': event})
    else:
        messages.error(request, 'You are not authorized to view this page')
        return redirect('index')


def manageEvents(request):
    if request.user.is_superuser:
        events = Event.objects.all()
        return render(request, 'manageEvents.html', {'events': events})
    else:
        messages.error(request, 'You are not authorized to view this page')
        return redirect('index')


def deleteEvent(request, event_id):
    if request.user.is_superuser:
        event = Event.objects.get(id=event_id)
        event.delete()
        messages.success(request, 'Event Deleted Successfully')
        return redirect('manageEvents')
    else:
        messages.error(request, 'You are not authorized to view this page')
        return redirect('index')


def eventStudents(request, eventID):
    if request.user.is_superuser:
        event = Event.objects.get(id=eventID)
        # all skills list
        skillSet = skill.objects.all()
        # students in event many field
        students = event.profiles.all()
        if request.method == 'POST':
            if 'add-btn' in request.POST:
                rollNumber = request.POST['rollNumber'].lower()
                if not User.objects.filter(username=rollNumber).exists():
                    user = None
                else:
                    user = User.objects.get(username=rollNumber)

                if user is None:
                    messages.error(request, 'Student does not exist')
                    return redirect('eventID', eventID=eventID)
                else:
                    student = Student.objects.get(rollNumber=user)
                    if student in event.profiles.all():
                        messages.error(request, 'Student already Enrolled in this event')
                        return redirect('eventID', eventID=eventID)
                    else:
                        event.profiles.add(student)
                        event.save()
                        messages.success(request,
                                         f'{student.rollNumber.first_name} {student.rollNumber.last_name} Added Successfully')
                        return redirect('eventID', eventID=eventID)
            elif 'bulk-btn' in request.POST:
                # 4 fields 1.skill 2.branch 3.percentage 4.year
                skillN = request.POST['skill']
                branch = request.POST['branch']
                percentage = request.POST['percentage']
                year = request.POST['year']
                print(skill, branch)
                # combinations of skill,branch,percentage,year
                # year with GradYear, percentage with GradPercentage, PucPercentage, SscPercentage
                if skillN == "" and branch == "":
                    students = Student.objects.filter(GradYear=year, status=True, GradPercentage__gte=percentage)
                    print(students)
                    l = 0
                    for student in students:
                        if student in event.profiles.all():
                            continue
                        else:
                            event.profiles.add(student)
                            event.save()
                            l += 1
                    messages.success(request, f'{l} New Students Added Successfully')
                    return redirect('eventID', eventID=eventID)
                elif skillN == "" and branch != "":
                    students = Student.objects.filter(GradYear=year, status=True, GradPercentage__gte=percentage,
                                                      GradBranch=branch)
                    l = 0
                    for student in students:
                        if student in event.profiles.all():
                            continue
                        else:
                            event.profiles.add(student)
                            event.save()
                            l += 1
                    messages.success(request, f'{l} New Students Added Successfully')
                    return redirect('eventID', eventID=eventID)
                elif skillN != "" and branch == "":
                    students = Student.objects.filter(GradYear=year, status=True, GradPercentage__gte=percentage,
                                                      skills__skillName=skillN)
                    print(students)
                    l = 0
                    for student in students:
                        if student in event.profiles.all():
                            continue
                        else:
                            event.profiles.add(student)
                            event.save()
                            l += 1
                    messages.success(request, f'{l} New Students Added Successfully')
                    return redirect('eventID', eventID=eventID)
                elif skillN != "" and branch != "":
                    students = Student.objects.filter(GradYear=year, status=True, GradPercentage__gte=percentage,
                                                      GradBranch=branch, skills__skillName=skillN)

                    l = 0
                    for student in students:
                        if student in event.profiles.all():
                            continue
                        else:
                            event.profiles.add(student)
                            event.save()
                            l += 1
                    messages.success(request, f'{l} New Students Added Successfully')
                    return redirect('eventID', eventID=eventID)
            else:
                messages.error(request, 'Invalid Request')
                return redirect('eventID', eventID=eventID)

        else:
            return render(request, 'add.html', {'students': students, 'event': event, 'skillSet': skillSet})
    else:
        messages.error(request, 'You are not authorized to view this page')
        return redirect('index')


def removeStudentFromEvent(request, event_id, roll_number):
    if request.user.is_superuser:
        event = Event.objects.get(id=event_id)
        user = User.objects.get(username=roll_number)
        student = Student.objects.get(rollNumber=user)
        student.placed = False
        event.profiles.remove(student)
        event.selected.remove(student)
        event.save()

        messages.success(request, f'{user.first_name} {user.last_name} Removed Successfully')
        return redirect('eventID', eventID=event_id)
    else:
        messages.error(request, 'You are not authorized to view this page')
        return redirect('index')


def sendMail(request, ID):
    # send mail to company mail with event details and Event Code Highlighted
    if request.user.is_superuser:
        event = Event.objects.get(id=ID)
        subject = 'Event Details'
        # hightlight event code
        message = f'Event Name: {event.title}\nEvent Description: {event.description}\nEvent Date: {event.date}\nEvent Venue: {event.venue}\nUse below Link to at out website\nWebSite:https://campus-connect.com\nEvent Code: {event.eventCode}'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [event.email]
        send_mail(subject, message, email_from, recipient_list)
        messages.success(request, 'Mail Sent Successfully')
        return redirect('eventID', eventID=ID)
    else:
        messages.error(request, 'You are not authorized to view this page')
        return redirect('index')


def manageStudents(request):
    if request.user.is_superuser:
        students = Student.objects.all().order_by('status')
        if request.method == 'POST':
            roll_number = request.POST.get('rollNumber').lower()
            if 'block-btn' in request.POST:
                if not User.objects.filter(username=roll_number).exists():
                    user = None
                else:
                    user = User.objects.get(username=roll_number)
                if user is not None:
                    student = Student.objects.get(rollNumber=user)
                    if student.status:
                        student.status = False
                        student.save()
                        messages.success(request, 'User Blocked')
                        return redirect('manageStudents')
                    else:
                        messages.info(request, 'User is already blocked')
                        return redirect('manageStudents')
                else:
                    messages.error(request, 'User does not exist')
                    return redirect('manageStudents')
            elif 'delete-btn' in request.POST:
                # check wheather roll_number is in User table or not in username field
                if not User.objects.filter(username=roll_number).exists():
                    user = None
                else:
                    user = User.objects.get(username=roll_number)
                if user is not None:
                    user.delete()
                    # user.save()
                    messages.success(request, 'User Deleted')
                    return redirect('manageStudents')
                else:
                    messages.error(request, 'User does not exist')
                    return redirect('manageStudents')
            elif 'unblock-btn' in request.POST:
                if not User.objects.filter(username=roll_number).exists():
                    user = None
                else:
                    user = User.objects.get(username=roll_number)
                if user is not None:
                    student = Student.objects.get(rollNumber=user)
                    if student.status:
                        messages.error(request, 'User is already unblocked')
                        return redirect('manageStudents')
                    else:
                        student.status = True
                        student.save()
                        messages.success(request, 'User Unblocked')
                        return redirect('manageStudents')
                else:
                    messages.error(request, 'User does not exist')
                    return redirect('manageStudents')
            else:
                messages.error(request, 'Invalid Request')
                return redirect('manageStudents')
        return render(request, 'manageUsers.html', {'students': students})
    else:
        messages.error(request, 'You are not authorized to view this page')
        return redirect('index')


def blockUser(request, roll_number):
    if request.user.is_superuser:
        user = User.objects.get(username=roll_number)
        student = Student.objects.get(rollNumber=user)
        if student.status:
            student.status = False
            student.save()
            messages.success(request, 'User Blocked')
            return redirect('manageStudents')
        else:
            messages.info(request, 'User is already blocked')
            return redirect('manageStudents')

    else:
        messages.error(request, 'You are not authorized to view this page')
        return redirect('login')


def unblockUser(request, roll_number):
    if request.user.is_superuser:
        user = User.objects.get(username=roll_number)
        student = Student.objects.get(rollNumber=user)
        if student.status:
            messages.error(request, 'User is already unblocked')
            return redirect('manageStudents')
        else:
            student.status = True
            student.save()
            messages.success(request, 'User Unblocked')
            return redirect('manageStudents')
    else:
        messages.error(request, 'You are not authorized to view this page')
        return redirect('login')


def deleteUser(request, roll_number):
    if request.user.is_superuser:
        user = User.objects.get(username=roll_number)
        if user is not None:
            user.delete()
            messages.success(request, 'User Deleted Successfully')
            return redirect('manageStudents')
        else:
            messages.error(request, 'User does not exist')
            return redirect('manageStudents')
    else:
        messages.error(request, 'You are not authorized to view this page')
        return redirect('login')


def showEvent(request, event_code):
    event = Event.objects.get(eventCode=event_code)
    # check with today date start date and expiry date
    today = timezone.now().date()
    if event.expiryDate is not None:
        if event.expiryDate.date() < today:
            messages.error(request, 'Event Code Expired')
            return redirect('index')
        if event.date.date() > today:
            messages.error(request, 'Event is not started yet')
            return redirect('index')
    if request.user.is_authenticated:
        if event.profiles.filter(rollNumber=request.user).exists():
            messages.error(request, 'students are not allowed to view this page')
            return redirect('login')
    return render(request, 'list.html', {'event': event})


def showProfile(request, event_code, roll_number):
    user = User.objects.get(username=roll_number)
    student = Event.objects.get(eventCode=event_code).profiles.get(rollNumber=user)
    event_code = Event.objects.get(eventCode=event_code)
    return render(request, 'student.html', {'student': student, 'event_code': event_code})


def checkStudent(request, roll_number):
    if request.user.is_superuser:
        if User.objects.filter(username=roll_number).exists():
            if Student.objects.filter(rollNumber=User.objects.get(username=roll_number)).exists():
                student = Student.objects.get(rollNumber=User.objects.get(username=roll_number))
                return render(request, 'student.html', {'student': student})
            else:
                messages.error(request, 'Student does not exist')
                return redirect('manageStudents')
        else:
            messages.error(request, 'Student does not exist')
            return redirect('manageStudents')
    else:
        messages.error(request, 'You are not authorized to view this page')
        return redirect('login')


def select_student(request, event_code, roll_number):
    if Event.objects.filter(eventCode=event_code).exists():
        event = Event.objects.get(eventCode=event_code)
        if User.objects.filter(username=roll_number).exists():
            if Student.objects.filter(rollNumber=User.objects.get(username=roll_number)).exists():
                student = Student.objects.get(rollNumber=User.objects.get(username=roll_number))
                if student in event.selected.all():
                    messages.error(request, 'Student already selected')
                    return redirect('showEvent', event_code=event_code)
                else:
                    event.selected.add(student)
                    event.save()
                    student.status = False
                    student.save()
                    messages.success(request, 'Student Selected Successfully')
                    return redirect('showEvent', event_code=event_code)
            else:
                messages.error(request, 'Student does not exist')
                return redirect('showEvent', event_code=event_code)
        else:
            messages.error(request, 'Student does not Registered')
            return redirect('showEvent', event_code=event_code)
    else:
        messages.error(request, 'Event does not exist')
        return redirect('index')


def unselect_student(request, event_code, roll_number):
    if Event.objects.filter(eventCode=event_code).exists():
        event = Event.objects.get(eventCode=event_code)
        if User.objects.filter(username=roll_number).exists():
            if Student.objects.filter(rollNumber=User.objects.get(username=roll_number)).exists():
                student = Student.objects.get(rollNumber=User.objects.get(username=roll_number))
                if student in event.selected.all():
                    event.selected.remove(student)
                    event.save()
                    messages.info(request, 'Student dropped Successfully')
                    return redirect('showEvent', event_code=event_code)
                else:
                    messages.error(request, 'Student is not in selected list')
                    return redirect('showEvent', event_code=event_code)
            else:
                messages.error(request, 'Student does not exist')
                return redirect('showEvent', event_code=event_code)
        else:
            messages.error(request, 'Student does not Registered')
            return redirect('showEvent', event_code=event_code)
    else:
        messages.error(request, 'Event does not exist')
        return redirect('index')


def send_report(request, event_code):
    if Event.objects.filter(eventCode=event_code).exists():
        event = Event.objects.get(eventCode=event_code)
        subject = 'Event Report'
        message = f'Dear TPO of SVREC,\n Greetings of the day,\n I would like ti share the report of recent Hiring,\nEvent Name: {event.title}\nEvent Description: {event.description}\nEvent Date: {event.date.date()}\nEvent Venue: {event.venue}\n\nTotal Selected Students: {event.selected.count()}\nTotal Students: {event.profiles.count()}\n\n\n Kindly Go through Your Dashboard to see the details.\nThank You\nRegards\nTeam Campus-Connect'
        email_from = settings.EMAIL_HOST_USER
        # get all admins emails
        admins = User.objects.filter(is_superuser=True)
        recipient_list = []
        for admin in admins:
            recipient_list.append(admin.email)
        if len(recipient_list) == 0:
            messages.error(request, 'No Admins Found')
            return redirect('showEvent', event_code=event_code)
        else:
            send_mail(subject, message, email_from, recipient_list)
            messages.success(request, 'Report Sent Successfully')
            return redirect('showEvent', event_code=event_code)
    else:
        messages.error(request, 'Event does not exist')
        return redirect('index')


def reports(request):
    if request.user.is_superuser:
        branches = Student.objects.values('GradBranch').distinct()
        total_students = Student.objects.all()
        total_count = total_students.count()
        selected_count = 0
        for student in total_students:
            if Event.objects.filter(selected=student).exists():
                student.placed = True
                student.save()
                selected_count += 1
            else:
                student.placed = False
                student.save()
        events = Event.objects.all().order_by('-date')
        if request.method == 'POST':
            branch = request.POST['branch']
            year = request.POST['year']
            if branch == 'all' and year == '':
                search_result = Student.objects.filter(placed=True)
            elif branch == 'all' and year != '':
                search_result = Student.objects.filter(GradYear=year, placed=True)
            elif branch != 'all' and year == '':
                search_result = Student.objects.filter(GradBranch=branch, placed=True)
            else:
                search_result = Student.objects.filter(GradBranch=branch, GradYear=year, placed=True)
            return render(request, 'reports.html',
                          {'events': events, 'total_count': total_count, 'selected_count': selected_count,
                           'branches': branches, 'search_result': search_result})
        return render(request, 'reports.html', {'events': events, 'total_count': total_count,
                                                'selected_count': selected_count, 'branches': branches})
    else:
        messages.error(request, 'You are not authorized to view this page')
        return redirect('index')
