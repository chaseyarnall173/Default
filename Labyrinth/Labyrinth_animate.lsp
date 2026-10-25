;; The Labyrinth - tilt animation for the 3D model built by Labyrinth_3D.scr
;; Load:  Manage tab > Applications > Load Application (APPLOAD), pick this
;;        file, Load (or drag the file onto the drawing).
;; Run:   type TILTDEMO   (TILTSPEED changes how fast it moves)
;; The model always ends back level.

(setq lab:C 5.75  lab:AZ -0.6  lab:B 11.5  lab:tilt 6  lab:ms 40)

(defun lab:board () (ssget "_X" '((8 . "FLOOR,RIM-FRONT,RIM-BACK,RIM-LEFT,RIM-RIGHT,WALLS,BRACKET-LEFT,BRACKET-RIGHT,TRAPDOOR-FLAP,TRAPDOOR-SERVO,BALL,HORN-1,TRAY-FRONT,TRAY-BACK,TRAY-LEFT,TRAY-RIGHT,TRAY-FLOOR,LABELS"))))
(defun lab:frame () (ssget "_X" '((8 . "FRAME-LEFT,FRAME-RIGHT,FRAME-FRONT,FRAME-BACK,FRAME-BAY,SERVO-1,PIN-AXIS1,HORN-2"))))

;; axis 1 runs left-right under the board; it rides on the frame, so after
;; the frame has turned b degrees on axis 2 its end points move too
(defun lab:axis1 (b / r)
  (setq r (* pi (/ b 180.0)))
  (list (list (+ lab:C (* (- 0 lab:C) (cos r))) lab:C
              (- lab:AZ (* (- 0 lab:C) (sin r))))
        (list (+ lab:C (* (- lab:B lab:C) (cos r))) lab:C
              (- lab:AZ (* (- lab:B lab:C) (sin r))))))

(defun lab:turn (sets p1 p2 ang)
  (command "_.ROTATE3D")
  (foreach s sets (if s (command s)))
  (command "" p1 p2 ang "_.DELAY" lab:ms))

;; swing one axis 0 -> +tilt -> -tilt -> 0, one degree per step
(defun lab:swing (sets p1 p2)
  (repeat (fix lab:tilt) (lab:turn sets p1 p2 1))
  (repeat (fix (* 2 lab:tilt)) (lab:turn sets p1 p2 -1))
  (repeat (fix lab:tilt) (lab:turn sets p1 p2 1)))

(defun c:TILTDEMO (/ echo snap board frame a2a a2b ax1)
  (setq echo (getvar "CMDECHO") snap (getvar "OSMODE"))
  (setvar "CMDECHO" 0) (setvar "OSMODE" 0)   ; snaps would move the axis points
  (setq board (lab:board) frame (lab:frame))
  (setq a2a (list lab:C 0.0 lab:AZ) a2b (list lab:C 1.0 lab:AZ))
  (princ "\n1) servo 1 only: the board tips front/back, the frame stays still")
  (setq ax1 (lab:axis1 0))
  (lab:swing (list board) (car ax1) (cadr ax1))
  (princ "\n2) servo 2 only: the frame tips left/right and carries the board")
  (lab:swing (list board frame) a2a a2b)
  (princ "\n3) both: frame tipped, then the board tips inside it")
  (repeat (fix lab:tilt) (lab:turn (list board frame) a2a a2b 1))
  (setq ax1 (lab:axis1 lab:tilt))
  (lab:swing (list board) (car ax1) (cadr ax1))
  (repeat (fix lab:tilt) (lab:turn (list board frame) a2a a2b -1))
  (setvar "CMDECHO" echo) (setvar "OSMODE" snap)
  (princ "\nDone - back to level.")
  (princ))

(defun c:TILTSPEED (/ v)
  (setq v (getint (strcat "\nPause per step in ms <" (itoa lab:ms) ">: ")))
  (if v (setq lab:ms v))
  (princ))

(princ "\nLabyrinth animation loaded - type TILTDEMO.")
(princ)
