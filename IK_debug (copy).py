# -*- coding: utf-8 -*-

from sympy import *
from time import time
from mpmath import radians
import tf
import pdb

'''
Format of test case is [ [[EE position],[EE orientation as quaternions]],[WC location],[joint angles]]
You can generate additional test cases by setting up your kuka project and running `$ roslaunch kuka_arm forward_kinematics.launch`
From here you can adjust the joint angles to find thetas, use the gripper to extract positions and orientation (in quaternion xyzw) and lastly use link 5
to find the position of the wrist center. These newly generated test cases can be added to the test_cases dictionary.
'''

test_cases = {1:[[[2.16135,-1.42635,1.55109],
                  [0.708611,0.186356,-0.157931,0.661967]],
                  [1.89451,-1.44302,1.69366],
                  [-0.65,0.45,-0.36,0.95,0.79,0.49]],
              2:[[[-0.56754,0.93663,3.0038],
                  [0.62073, 0.48318,0.38759,0.480629]],
                  [-0.638,0.64198,2.9988],
                  [-0.79,-0.11,-2.33,1.94,1.14,-3.68]],
              3:[[[-1.3863,0.02074,0.90986],
                  [0.01735,-0.2179,0.9025,0.371016]],
                  [-1.1669,-0.17989,0.85137],
                  [-2.99,-0.12,0.94,4.06,1.29,-4.12]],
              4:[[[2.1529,0,1.94653],
                  [0,-0.999148353,0,1]],
                  [2.15286,0,1.94645],
                  [0,0,0,0,0,0]],
              5:[]}


def rot_x(q):
    R_x = Matrix([[ 1,              0,        0],
                  [ 0,         cos(q),  -sin(q)],
                  [ 0,         sin(q),  cos(q)]])
    
    return R_x
    
def rot_y(q):              
    R_y = Matrix([[ cos(q),        0,  sin(q)],
                  [      0,        1,       0],
                  [-sin(q),        0, cos(q)]])
    
    return R_y

def rot_z(q):    
    R_z = Matrix([[ cos(q),  -sin(q),       0],
                  [ sin(q),   cos(q),       0],
                  [      0,        0,       1]])
    
    return R_z

def trans_matrix(alpha, a, d, q):
    T = Matrix([[            cos(q),           -sin(q),           0,             a],
                [ sin(q)*cos(alpha), cos(q)*cos(alpha), -sin(alpha), -sin(alpha)*d],
                [ sin(q)*sin(alpha), cos(q)*sin(alpha),  cos(alpha),  cos(alpha)*d],
                [                 0,                 0,           0,             1]])
    return T

def rad(deg):
    """ Convert degree to radian.
    """
    return deg * pi/180.

def dist(original_pos, target_pos):
    """ Find distance from given original and target position.
    """
    vector = target_pos - original_pos
    return sqrt((vector.T * vector)[0])

def test_code(test_case):
    ## Set up code
    ## Do not modify!
    x = 0
    class Position:
        def __init__(self,EE_pos):
            self.x = EE_pos[0]
            self.y = EE_pos[1]
            self.z = EE_pos[2]
    class Orientation:
        def __init__(self,EE_ori):
            self.x = EE_ori[0]
            self.y = EE_ori[1]
            self.z = EE_ori[2]
            self.w = EE_ori[3]

    position = Position(test_case[0][0])
    orientation = Orientation(test_case[0][1])

    class Combine:
        def __init__(self,position,orientation):
            self.position = position
            self.orientation = orientation

    comb = Combine(position,orientation)

    class Pose:
        def __init__(self,comb):
            self.poses = [comb]

    req = Pose(comb)
    start_time = time()
    
    ########################################################################################
    ## 

    ## Insert IK code here!
    # Create symbols
    q1, q2, q3, q4, q5, q6, q7 = symbols('q1:8')
    d1, d2, d3, d4, d5, d6, d7 = symbols('d1:8')
    a0, a1, a2, a3, a4, a5, a6 = symbols('a0:7')
    alpha0, alpha1, alpha2, alpha3, alpha4, alpha5, alpha6 = symbols('alpha0:7')

    # Create Modified DH parameters
    s = {alpha0:        0, a0:      0, d1:  0.75, q1: q1,
         alpha1: rad(-90), a1:   0.35, d2:     0, q2: q2-rad(90),
         alpha2:        0, a2:   1.25, d3:     0, q3: q3,
         alpha3: rad(-90), a3: -0.054, d4:  1.50, q4: q4,
         alpha4:  rad(90), a4:      0, d5:     0, q5: q5,
         alpha5: rad(-90), a5:      0, d6:     0, q6: q6,
         alpha6:        0, a6:      0, d7: 0.303, q7: 0
    }

    # Define Modified DH Transformation matrix
    T0_1 = trans_matrix(alpha0, a0, d1, q1).subs(s)
    T1_2 = trans_matrix(alpha1, a1, d2, q2).subs(s)
    T2_3 = trans_matrix(alpha2, a2, d3, q3).subs(s)
    T3_4 = trans_matrix(alpha3, a3, d4, q4).subs(s)
    T4_5 = trans_matrix(alpha4, a4, d5, q5).subs(s)
    T5_6 = trans_matrix(alpha5, a5, d6, q6).subs(s)
    T6_EE = trans_matrix(alpha6, a6, d7, q7).subs(s)

    # Create individual transformation matrices
    T0_2 = simplify(T0_1 * T1_2).subs(s)
    T0_3 = simplify(T0_2 * T2_3).subs(s)
    # T0_4 = simplify(T0_3 * T3_4)
    # # Wrist Center
    # T0_5 = simplify(T0_4 * T4_5)
    # T0_6 = simplify(T0_5 * T5_6)
    # End Effector
    T0_EE = simplify(T0_3 * T3_4 * T4_5 * T5_6 * T6_EE)

    print("\nTime to create transformation matrices: %04.4f seconds" % (time() - start_time))

    # From walkthrough. Update all lines below that use T.
    # No difference in result and performance compared with the above.
    # T0_G = T0_1 * T1_2 * T2_3 * T3_4 * T4_5 * T5_6 * T6_G

    # --- IK code ---

    ik_start_time = time()
    # Extract end-effector position and orientation from request
    # px,py,pz = end-effector position
    # roll, pitch, yaw = end-effector orientation
    px = req.poses[x].position.x
    py = req.poses[x].position.y
    pz = req.poses[x].position.z

    (roll, pitch, yaw) = tf.transformations.euler_from_quaternion(
        [req.poses[x].orientation.x, req.poses[x].orientation.y,
            req.poses[x].orientation.z, req.poses[x].orientation.w])

    ### Your IK code here

    r, p, y = symbols('r p y')

    R_x = rot_x(r)
    R_y = rot_y(p)
    R_z = rot_z(y)
    # Rotation matrix of gripper
    R_EE = R_x * R_y * R_z
    # print R_G
    # Matrix([[r11, r12, r13],
    #         [r21, r22, r23],
    #         [r31, r32, r33]])

    # Compensate for rotation discrepancy between DH parameters and Gazebo
    Rot_err = rot_z(rad(180)) * rot_y(rad(-90))

    # print Rot_err
    # Matrix([[0,  0, 1],
    #         [0, -1, 0],
    #         [1,  0, 0]])

    R_EE = R_EE * Rot_err
    # print R_EE
    # Matrix([[r13, -r12, r11],
    #         [r23, -r22, r21],
    #         [r33, -r32, r31])

    R_EE = R_EE.subs({'r': roll, 'p': pitch, 'y': yaw})
    # Find wrist position with formula described in
    # https://classroom.udacity.com/nanodegrees/nd209/parts/7b2fd2d7-e181-401e-977a-6158c77bf816/modules/8855de3f-2897-46c3-a805-628b5ecf045b/lessons/91d017b1-4493-4522-ad52-04a74a01094c/concepts/a1abb738-84ee-48b1-82d7-ace881b5aec0
    G = Matrix([[px], [py], [pz]])
    # d7: Length of WC to G
    WC = G - (s[d6] + s[d7]) * R_EE[:, 2]

    # Calculate joint angles using Geometric IK method

    # Relevant lesson:
    # https://classroom.udacity.com/nanodegrees/nd209/parts/7b2fd2d7-e181-401e-977a-6158c77bf816/modules/8855de3f-2897-46c3-a805-628b5ecf045b/lessons/87c52cd9-09ba-4414-bc30-24ae18277d24/concepts/8d553d46-d5f3-4f71-9783-427d4dbffa3a
    theta1 = atan2(WC[1], WC[0])
    # print(WC)
    # print(theta1)


    # https://www.mathsisfun.com/algebra/trig-solving-triangles.html

    # Position of link 2 (O2)
    # T0_2 = T0_1 * T1_2
    O2 = T0_2.subs({"q1": theta1})[:3, 3]

    # c is then the distance between O2 and WC
    c = dist(O2, WC)
    # This was the method shown in the walkthrough. It resulted in exactly same
    # value and running time, so we don't use it.
    # c = sqrt(pow((sqrt(WC[0]*WC[0] + WC[1]*WC[1]) - 0.35), 2) + pow((WC[2] - 0.75), 2))

    a = s[a2]
    b = s[d4]

    # d is z position of WC minus Z position of O2.
    d = WC[2] - O2[2]
    e = sqrt(c**2 - d **2)

    delta = atan2(d, e)
    beta = acos((a*a + c*c - b*b) / (2 * a * c))
    theta2 = rad(90) - beta - delta
    # theta2 = rad(90) - beta - atan2(WC[2]-0.75, sqrt(WC[0]*WC[0] + WC[1]*WC[1]) - 0.35)

    alpha = acos((b*b + c*c - a*a) / (2 * b * c))
    gamma = (rad(180) - alpha - beta)
    # From walkthrough, no difference.
    # gamma = acos((a*a + b*b - c*c) / (2 * a * b))
    theta3 = (rad(90) - alpha - (rad(180)-alpha-gamma))
    # theta3 = rad(90) - (alpha + 0.036)

    # The following is similar with (T0_1[:3,:3] * T1_2[:3,:3] * T2_3[:3,:3]).simplify()
    R0_3 = T0_3[:3,:3]
    # From walkthrough, no difference
    # R0_3 = T0_1[:3,:3] * T1_2[:3,:3] * T2_3[:3,:3]
    R3_6 = R0_3.inv("LU") * R_EE

    # Steps from https://classroom.udacity.com/nanodegrees/nd209/parts/7b2fd2d7-e181-401e-977a-6158c77bf816/modules/8855de3f-2897-46c3-a805-628b5ecf045b/lessons/87c52cd9-09ba-4414-bc30-24ae18277d24/concepts/a124f98b-1ed5-45f5-b8eb-6c40958c1a6b
    # r31 = R3_6[2,0]
    # r11 = R3_6[0,0]
    # r21 = R3_6[1,0]
    # r32 = R3_6[2,1]
    # r33 = R3_6[2,2]
    # theta5  = atan2(-r31, sqrt(r11 * r11 + r21 * r21))
    # theta6 = atan2(r32, r33)
    # theta4 = atan2(r21, r11)

    # Steps from walkthrough - Got larger theta errors, somehow, but lower
    # overall errors.
    theta4 = atan2(R3_6[2,2], R3_6[0,2])
    theta5  = atan2(sqrt(R3_6[0,2]*R3_6[0,2] + R3_6[2,2]*R3_6[2,2]),R3_6[1,2])
    theta6 = atan2(-R3_6[1,1],R3_6[1,0])

    theta2 = theta2.evalf()
    theta3 = theta3.evalf()
    theta4 = theta4.evalf(subs={"q1":theta1, "q2":theta2, "q3":theta3})
    theta5 = theta5.evalf(subs={"q1":theta1, "q2":theta2, "q3":theta3})
    theta6 = theta6.evalf(subs={"q1":theta1, "q2":theta2, "q3":theta3})
    print("\nTime to create thetas: %04.4f seconds" % (time() - ik_start_time))

    # 
    # theta2 = atan2(s[""])



    ## 
    ########################################################################################
    
    ########################################################################################
    ## For additional debugging add your forward kinematics here. Use your previously calculated thetas
    ## as the input and output the position of your end effector as your_ee = [x,y,z]

    ## (OPTIONAL) YOUR CODE HERE!

    EE = T0_EE.evalf(subs={"q1":theta1, "q2":theta2, "q3":theta3,
                           "q4":theta4, "q5":theta5, "q6":theta6})[:3, 3]

    ## End your code input for forward kinematics here!
    ########################################################################################

    ## For error analysis please set the following variables of your WC location and EE location in the format of [x,y,z]
    your_wc = WC # <--- Load your calculated WC values in this array
    your_ee = EE # <--- Load your calculated end effector value from your forward kinematics
    ########################################################################################

    ## Error analysis
    print ("\nTotal run time to calculate joint angles from pose is %04.4f seconds" % (time()-start_time))

    # Find WC error
    if not(sum(your_wc)==3):
        wc_x_e = abs(your_wc[0]-test_case[1][0])
        wc_y_e = abs(your_wc[1]-test_case[1][1])
        wc_z_e = abs(your_wc[2]-test_case[1][2])
        wc_offset = sqrt(wc_x_e**2 + wc_y_e**2 + wc_z_e**2)
        print ("\nWrist error for x position is: %04.8f" % wc_x_e)
        print ("Wrist error for y position is: %04.8f" % wc_y_e)
        print ("Wrist error for z position is: %04.8f" % wc_z_e)
        print ("Overall wrist offset is: %04.8f units" % wc_offset)

    # Find theta errors
    t_1_e = abs(theta1-test_case[2][0])
    t_2_e = abs(theta2-test_case[2][1])
    t_3_e = abs(theta3-test_case[2][2])
    t_4_e = abs(theta4-test_case[2][3])
    t_5_e = abs(theta5-test_case[2][4])
    t_6_e = abs(theta6-test_case[2][5])
    print ("\nTheta 1 error is: %04.8f" % t_1_e)
    print ("Theta 2 error is: %04.8f" % t_2_e)
    print ("Theta 3 error is: %04.8f" % t_3_e)
    print ("Theta 4 error is: %04.8f" % t_4_e)
    print ("Theta 5 error is: %04.8f" % t_5_e)
    print ("Theta 6 error is: %04.8f" % t_6_e)
    print ("\n**These theta errors may not be a correct representation of your code, due to the fact \
           \nthat the arm can have muliple positions. It is best to add your forward kinmeatics to \
           \nconfirm whether your code is working or not**")
    print (" ")

    # Find FK EE error
    if not(sum(your_ee)==3):
        ee_x_e = abs(your_ee[0]-test_case[0][0][0])
        ee_y_e = abs(your_ee[1]-test_case[0][0][1])
        ee_z_e = abs(your_ee[2]-test_case[0][0][2])
        ee_offset = sqrt(ee_x_e**2 + ee_y_e**2 + ee_z_e**2)
        print ("\nEnd effector error for x position is: %04.8f" % ee_x_e)
        print ("End effector error for y position is: %04.8f" % ee_y_e)
        print ("End effector error for z position is: %04.8f" % ee_z_e)
        print ("Overall end effector offset is: %04.8f units \n" % ee_offset)




if __name__ == "__main__":
    # Change test case number for different scenarios
    test_case_number = 4

    test_code(test_cases[test_case_number])
