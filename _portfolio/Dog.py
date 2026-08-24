---
title: "Turtle"
excerpt: "Short description of portfolio item number 1<br/><img src='/images/500x300.png'>"
collection: portfolio
---

import turtle as t
t.screensize(500, 500)
# 【 head outline 】
t.pensize(5)
t.home()
t.seth(0)
t.pd() #pendown
t.color('#3a3420')
t.circle(20, 80) # 0
t.circle(200, 30) # 1
t.circle(30, 60) # 2
t.circle(200, 29.5) # 3
t.color('#3a3420')
t.circle(20, 60) # 4
t.circle(-150, 22) # 5
t.circle(-50, 10) # 6
t.circle(50, 70) # 7
# determine the approximate position of the nose t.xcor and t. ycor the position of the tortoise at the beginning
x_nose = t.xcor()
y_nose = t.ycor()
t.circle(30, 62) # 8
t.circle(200, 15) # 9
# 【 nose 】
t.pu() #penup
t.goto(x_nose, y_nose + 25)
t.seth(90)
t.pd()
t.begin_fill()
t.circle(8)
t.end_fill()
# 【 eye 】
t.pu()
t.goto(x_nose + 55, y_nose + 60)
t.seth(90)
t.pd()
t.begin_fill()
t.circle(12)
t.end_fill()
# 【 ear 】
t.pu()
t.color('#3a3420')
t.goto(x_nose + 100, y_nose + 110)
t.seth(182)
t.pd()
t.circle(15, 45)
t.color('#3a3420')
t.circle(10, 15)
t.circle(90, 70)
t.circle(25, 110)
t.rt(4)
t.circle(90, 70)
t.circle(10, 15)
t.color('#3a3420')
t.circle(15, 45)
# 【 body 】
t.pu()
t.color('#3a3420')
t.goto(x_nose + 90, y_nose - 30)
t.seth(-130)
t.pd()
t.circle(250, 28)
t.circle(10, 140)
t.circle(-250, 25)
t.circle(-200, 25)
t.circle(-50, 85)
t.circle(8, 145)
t.circle(90, 45)
t.circle(550, 5)
# 【 tail 】
t.seth(0)
t.circle(60, 85)
t.circle(40, 65)
t.circle(40, 60)
t.lt(150) #left
t.circle(-40, 90)
t.circle(-25, 100)
t.lt(5)
t.fd(20)
t.circle(10, 60)
# 【 back 】
t.rt(80) #right
t.circle(200, 35)
# 【 collar 】
t.pensize(25)
t.color('#bf360c')
t.lt(10)
t.circle(-200, 25)
# 【 bell 】
t.pu()
t.fd(18)
t.lt(90)
t.fd(18)
t.pensize(6)
t.seth(35) #setheading
t.color('#FDAF17')
t.begin_fill()
t.lt(135)
t.fd(6)
t.right(180) # brush turn around
t.circle(6, -180)
t.backward(8)
t.right(90)
t.forward(6)
t.circle(-6, 180)
t.fd(15)
t.end_fill()
# 【 front calf 】
t.pensize(5)
t.pu()
t.color('#3a3420')
t.goto(x_nose + 100, y_nose - 125)
t.pd()
t.seth(-50)
t.fd(25)
t.circle(10, 150)
t.fd(25)
# 【 posterior calf 】
t.pensize(4)
t.pu()
t.goto(x_nose + 314, y_nose - 125)
t.pd()
t.seth(-95)
t.fd(25)
t.circle(-5, 150)
t.fd(2)
t.hideturtle()
t.bgcolor('#ece4d4')
# mouth
t.pu()
t.goto(x_nose + 5, y_nose + 5)
t.seth(-60)
t.pensize(4)
t.color('black')
t.pd()
t.circle(25, 120)
t.pu()
# tongue
t.pu()
t.goto(x_nose + 15, y_nose - 2)
t.seth(0)
t.color('#e84e40')
t.pd()
t.begin_fill()
t.circle(8, 180)
t.left(180)
t.circle(8, 180)
t.end_fill()
t.pu()
t.done()



