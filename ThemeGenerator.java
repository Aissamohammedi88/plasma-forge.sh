// PLASMA FORGE — SVG pattern generator
// Args: seed voronoi_points width height color1,color2,...
// Sortie : SVG sur stdout (pattern background unique)

import java.util.Random;

public class ThemeGenerator {
    public static void main(String[] args) {
        long seed = args.length > 0 ? parseSeed(args[0]) : System.currentTimeMillis();
        int points = args.length > 1 ? Integer.parseInt(args[1]) : 12;
        int width = args.length > 2 ? Integer.parseInt(args[2]) : 1920;
        int height = args.length > 3 ? Integer.parseInt(args[3]) : 1080;
        String[] defaultPalette = {"#FF006E", "#FB5607", "#FFBE0B", "#8338EC", "#3A86FF"};
        String[] palette = args.length > 4 ? args[4].split(",") : defaultPalette;

        Random rng = new Random(seed);
        StringBuilder svg = new StringBuilder();

        svg.append(String.format(
            "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"%d\" height=\"%d\" viewBox=\"0 0 %d %d\" preserveAspectRatio=\"xMidYMid slice\">",
            width, height, width, height));

        // Defs : filtres + gradients
        svg.append("<defs>");
        svg.append("<filter id=\"blur\"><feGaussianBlur stdDeviation=\"80\"/></filter>");
        svg.append("<filter id=\"grain\"><feTurbulence type=\"fractalNoise\" baseFrequency=\"0.9\" numOctaves=\"3\"/></filter>");
        // Gradient linéaire diagonale
        svg.append("<linearGradient id=\"diag\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\">");
        for (int i = 0; i < palette.length; i++) {
            float offset = (float) i / (palette.length - 1);
            svg.append(String.format("<stop offset=\"%f\" stop-color=\"%s\"/>", offset, palette[i]));
        }
        svg.append("</linearGradient></defs>");

        // Fond
        svg.append(String.format("<rect width=\"%d\" height=\"%d\" fill=\"#0a0a0f\"/>", width, height));

        // Plasma blobs (flous pour effet aurora)
        svg.append("<g filter=\"url(#blur)\">");
        for (int i = 0; i < points; i++) {
            int x = rng.nextInt(width);
            int y = rng.nextInt(height);
            int r = 200 + rng.nextInt(300);
            String color = palette[rng.nextInt(palette.length)];
            float opacity = 0.4f + rng.nextFloat() * 0.3f;
            svg.append(String.format(
                "<circle cx=\"%d\" cy=\"%d\" r=\"%d\" fill=\"%s\" opacity=\"%f\"/>",
                x, y, r, color, opacity));
        }
        svg.append("</g>");

        // Étoiles / points
        svg.append("<g opacity=\"0.25\">");
        for (int i = 0; i < 500; i++) {
            int x = rng.nextInt(width);
            int y = rng.nextInt(height);
            int r = 1 + rng.nextInt(2);
            svg.append(String.format("<circle cx=\"%d\" cy=\"%d\" r=\"%d\" fill=\"white\"/>", x, y, r));
        }
        svg.append("</g>");

        // Polygones géométriques (overlay subtil)
        svg.append("<g opacity=\"0.10\" stroke=\"white\" fill=\"none\" stroke-width=\"1\">");
        for (int i = 0; i < 40; i++) {
            int cx = rng.nextInt(width);
            int cy = rng.nextInt(height);
            int size = 30 + rng.nextInt(80);
            int sides = 3 + rng.nextInt(5);
            StringBuilder pts = new StringBuilder();
            for (int s = 0; s < sides; s++) {
                double angle = (2 * Math.PI * s) / sides - Math.PI / 2;
                int px = (int) (cx + size * Math.cos(angle));
                int py = (int) (cy + size * Math.sin(angle));
                if (s > 0) pts.append(" ");
                pts.append(px).append(",").append(py);
            }
            svg.append(String.format("<polygon points=\"%s\"/>", pts.toString()));
        }
        svg.append("</g>");

        // Lignes de connexion (réseau)
        svg.append("<g opacity=\"0.12\" stroke=\"white\" stroke-width=\"0.5\">");
        int[][] nodes = new int[15][2];
        for (int i = 0; i < 15; i++) {
            nodes[i][0] = rng.nextInt(width);
            nodes[i][1] = rng.nextInt(height);
        }
        for (int i = 0; i < 15; i++) {
            for (int j = i + 1; j < 15; j++) {
                int dx = nodes[i][0] - nodes[j][0];
                int dy = nodes[i][1] - nodes[j][1];
                int dist = (int) Math.sqrt(dx * dx + dy * dy);
                if (dist < 400) {
                    svg.append(String.format(
                        "<line x1=\"%d\" y1=\"%d\" x2=\"%d\" y2=\"%d\"/>",
                        nodes[i][0], nodes[i][1], nodes[j][0], nodes[j][1]));
                }
            }
        }
        svg.append("</g>");

        svg.append("</svg>");
        System.out.println(svg.toString());
    }

    private static long parseSeed(String s) {
        try { return Long.parseLong(s); }
        catch (NumberFormatException e) {
            long h = 0;
            for (byte b : s.getBytes()) h = h * 31 + b;
            return h;
        }
    }
}
