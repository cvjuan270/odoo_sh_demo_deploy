import datetime
from logging import getLogger

from odoo import api, fields, models

_logger = getLogger(__name__)


class SequenceDateRangeCreator(models.AbstractModel):
    _name = "tgr.sequence.date.range.creator"
    _description = "Sequence Date Range Creator"

    @api.model
    def create_sequence_date_ranges(
        self, sequence_code, num_periods=6, period_type="month"
    ):
        """
        Crea rangos de fechas para una secuencia específica.
        Args:
            sequence_code (str): Código de la secuencia para la que se crearán los rangos.
            num_periods (int): Número de periodos para los que se crearán rangos (por defecto: 3).
            period_type (str): Tipo de periodo ('month', 'quarter', 'year'). Por defecto: 'month'.

        Returns:
            list: Lista de IDs de los rangos creados.
        """
        sequence_id = self.env["ir.sequence"].search(
            [("code", "=", sequence_code)], limit=1
        )

        if not sequence_id:
            _logger.error(f"No se encontró la secuencia con código '{sequence_code}'")
            return []

        created_ranges = []
        today = fields.Date.context_today(self)

        for period_offset in range(num_periods):
            date_from, date_to = self._calculate_period_dates(
                today, period_offset, period_type
            )

            # Verificar si ya existe un rango para esta fecha y secuencia
            existing_range = self.env["ir.sequence.date_range"].search(
                [
                    ("sequence_id", "=", sequence_id.id),
                    ("date_from", "=", date_from),
                    ("date_to", "=", date_to),
                ],
                limit=1,
            )

            if existing_range:
                _logger.info(
                    f"Ya existe un rango para la secuencia '{sequence_id.name}' "
                    f"del {date_from} al {date_to}"
                )
                continue

            # Crear el nuevo rango de fechas
            try:
                new_range = self.env["ir.sequence.date_range"].create(
                    {
                        "sequence_id": sequence_id.id,
                        "date_from": date_from,
                        "date_to": date_to,
                        "number_next": 1,  # Número inicial de la secuencia
                    }
                )
                created_ranges.append(new_range.id)
                _logger.info(
                    f"Rango de fechas creado exitosamente para la secuencia '{sequence_id.name}' "
                    f"del {date_from} al {date_to}"
                )
            except Exception as e:
                _logger.error(
                    f"Error al crear el rango de fechas del {date_from} al {date_to}: {str(e)}"
                )

        return created_ranges

    def _calculate_period_dates(self, base_date, period_offset, period_type):
        """
        Calcula las fechas de inicio y fin para un periodo específico.

        Args:
            base_date (datetime.date): Fecha base para el cálculo.
            period_offset (int): Número de periodos a partir de la fecha base.
            period_type (str): Tipo de periodo ('month', 'quarter', 'year').

        Returns:
            tuple: (date_from, date_to) Fechas de inicio y fin del periodo.
        """
        if period_type == "month":
            return self._calculate_month_dates(base_date, period_offset)
        elif period_type == "quarter":
            return self._calculate_quarter_dates(base_date, period_offset)
        elif period_type == "year":
            return self._calculate_year_dates(base_date, period_offset)
        else:
            raise ValueError(f"Tipo de periodo no soportado: {period_type}")

    def _calculate_month_dates(self, base_date, month_offset):
        """Calcula las fechas para un periodo mensual."""
        # Calcular el mes y año para este rango
        target_month = base_date.month + month_offset
        target_year = base_date.year

        # Ajustar el año si el mes es mayor que 12
        while target_month > 12:
            target_month -= 12
            target_year += 1

        # Definir fechas de inicio y fin para el rango
        date_from = datetime.date(target_year, target_month, 1)

        # Calcular el último día del mes
        if target_month == 12:
            next_month = 1
            next_year = target_year + 1
        else:
            next_month = target_month + 1
            next_year = target_year

        date_to = datetime.date(next_year, next_month, 1) - datetime.timedelta(days=1)

        return date_from, date_to

    def _calculate_quarter_dates(self, base_date, quarter_offset):
        """Calcula las fechas para un periodo trimestral."""
        # Determinar el trimestre actual
        current_quarter = ((base_date.month - 1) // 3) + 1

        # Calcular el trimestre objetivo
        total_quarters = current_quarter + quarter_offset
        target_quarter = ((total_quarters - 1) % 4) + 1
        target_year = base_date.year + ((total_quarters - 1) // 4)

        # Mes de inicio del trimestre
        start_month = (target_quarter - 1) * 3 + 1

        # Definir fechas de inicio y fin para el rango
        date_from = datetime.date(target_year, start_month, 1)

        # Fechas de fin (último día del último mes del trimestre)
        end_month = start_month + 2
        if end_month == 12:
            next_month = 1
            next_year = target_year + 1
        else:
            next_month = end_month + 1
            next_year = target_year

        date_to = datetime.date(next_year, next_month, 1) - datetime.timedelta(days=1)

        return date_from, date_to

    def _calculate_year_dates(self, base_date, year_offset):
        """Calcula las fechas para un periodo anual."""
        target_year = base_date.year + year_offset

        date_from = datetime.date(target_year, 1, 1)
        date_to = datetime.date(target_year, 12, 31)

        return date_from, date_to

    @api.model
    def cron_create_sequence_date_ranges(
        self, sequence_code, num_periods=3, period_type="month"
    ):
        """
        Método para ser llamado desde un cron job.

        Args:
            sequence_code (str): Código de la secuencia.
            num_periods (int): Número de periodos.
            period_type (str): Tipo de periodo ('month', 'quarter', 'year').
        """
        self.create_sequence_date_ranges(sequence_code, num_periods, period_type)
