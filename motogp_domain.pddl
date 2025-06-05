(define (domain motogp_domain)
  (:requirements :strips :typing)
  (:types moto)

  (:predicates
    (benzina-ok ?m - moto)
    (elettronica-ok ?m - moto)
    (assetto-ok ?m - moto)
    (pronto ?m - moto)
    (tested ?m - moto)

  )

  ;; Ogni azione è indipendente

  (:action benzina
    :parameters (?m - moto)
    :precondition ()
    :effect (benzina-ok ?m)
  )

  (:action assetto
    :parameters (?m - moto)
    :precondition ()
    :effect (assetto-ok ?m)
  )

  (:action elettronica
    :parameters (?m - moto)
    :precondition ()
    :effect (elettronica-ok ?m)
  )

  ;; Azione finale: rende la moto pronta SOLO se ha fatto tutte le azioni selezionate
  (:action da-testare
    :parameters (?m - moto)
    :precondition (and
        (benzina-ok ?m)
        (elettronica-ok ?m)
        (assetto-ok ?m)
    )
    :effect (pronto ?m)
  )

  (:action test-moto
  :parameters (?m - moto)
  :precondition (pronto ?m)
  :effect (and (tested ?m))
)
)
