CREATE TABLE IF NOT EXISTS Recobros (
  Id_recobro BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  Id_entrada BIGINT UNSIGNED NOT NULL,
  Fecha_pago DATETIME NOT NULL,
  Minutos_excedidos INT NOT NULL,
  Importe FLOAT NOT NULL,
  CorteInc INT NOT NULL DEFAULT 0,
  PRIMARY KEY (Id_recobro),
  KEY Id_entrada (Id_entrada),
  CONSTRAINT Recobros_ibfk_1
    FOREIGN KEY (Id_entrada) REFERENCES Entradas (id)
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
