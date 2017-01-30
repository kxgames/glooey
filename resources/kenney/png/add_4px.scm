; for png in *.png; do if file $png | grep -q 45; then \gimp -b "$(cat add_4px.scm)" $png; fi; done      
; for png in *.png; do if file $png | grep -q 45; then echo $png; fi; done
(define img (car (gimp-image-list)))
(define path (car (gimp-image-get-filename img)))
(define w (car (gimp-image-width img)))
(define h (+ 4 (car (gimp-image-height img))))
(gimp-image-resize img w h 0 4)
(file-png-save-defaults 0 img (car (gimp-image-get-active-drawable img)) path path)
(gimp-quit 1)
