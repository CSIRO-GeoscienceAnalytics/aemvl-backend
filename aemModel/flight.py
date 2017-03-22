class Flight:
    _headers = None

    _lines = None

    def __init__(self, header, lines):
        self._headers = header
        self._lines = lines

    def get_headers(self):
        return self._headers

    def get_lines(self):
        return self._lines.values()

    def get_line(self, line_number):
        return self._lines[line_number]

    def get_extent(self):
        easting_min = float("inf")
        easting_max = float("-inf")
        northing_min = float("inf")
        northing_max = float("-inf")
        for line in self.get_lines():
            line_easting_min, line_easting_max, line_northing_min, line_northing_max = line.get_extent()

            easting_min = min(easting_min, line_easting_min)
            easting_max = max(easting_max, line_easting_max)
            northing_min = min(northing_min, line_northing_min)
            northing_max = max(northing_max, line_northing_max)

        return (easting_min, easting_max, northing_min, northing_max)

    def __str__(self):
        return "Not implemented."
        
    def to_json_friendly(self):
        lines = []
        for line in self.get_lines():
            lines.append(line.to_json_friendly())

        return {
            'flight': {
                'headers': self.get_headers(),
                'lines':   lines
            }
        }