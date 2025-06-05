(define (problem problema-motogp-2)
  (:domain motogp_domain)

  (:objects
    moto1 moto2 - moto
  )

  (:init
    
  )

  (:goal
    (and
          (benzina-ok moto1)
    (tested moto2)
    )
  )
)
