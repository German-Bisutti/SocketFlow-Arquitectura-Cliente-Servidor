-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 19-11-2026 a las 16:32:58
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `redes_tp_final`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `followers`
--

CREATE TABLE `followers` (
  `id` int(11) NOT NULL,
  `usuario` varchar(100) DEFAULT NULL,
  `nombre_follower` varchar(100) DEFAULT NULL,
  `fecha_guardado` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `followers`
--

INSERT INTO `followers` (`id`, `usuario`, `nombre_follower`, `fecha_guardado`) VALUES
(1, 'German-Bisutti', 'NiettoFran', '2026-11-18 19:31:02');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `repositorios`
--

CREATE TABLE `repositorios` (
  `id` int(11) NOT NULL,
  `usuario` varchar(100) DEFAULT NULL,
  `nombre_repo` varchar(255) DEFAULT NULL,
  `url_repo` varchar(255) DEFAULT NULL,
  `fecha_guardado` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `repositorios`
--

INSERT INTO `repositorios` (`id`, `usuario`, `nombre_repo`, `url_repo`, `fecha_guardado`) VALUES
(1, 'German-Bisutti', 'Desarrollo-de-Software', 'https://github.com/German-Bisutti/Desarrollo-de-Software', '2026-11-18 19:30:48'),
(2, 'German-Bisutti', 'E-commers-Indumentaria', 'https://github.com/German-Bisutti/E-commers-Indumentaria', '2026-11-18 19:30:48'),
(3, 'German-Bisutti', 'German-Bisutti', 'https://github.com/German-Bisutti/German-Bisutti', '2026-11-18 19:30:48'),
(4, 'German-Bisutti', 'Portafolio', 'https://github.com/German-Bisutti/Portafolio', '2026-11-18 19:30:48'),
(5, 'German-Bisutti', 'Rick-and-Morty', 'https://github.com/German-Bisutti/Rick-and-Morty', '2026-11-18 19:30:48'),
(6, 'German-Bisutti', 'SocketFlow-Arquitectura-Cliente-Servidor', 'https://github.com/German-Bisutti/SocketFlow-Arquitectura-Cliente-Servidor', '2026-11-18 19:30:48'),
(7, 'German-Bisutti', 'Videogames-Api', 'https://github.com/German-Bisutti/Videogames-Api', '2026-11-18 19:30:48');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL,
  `nombre_usuario` varchar(50) NOT NULL,
  `contrasena` varchar(64) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id`, `nombre_usuario`, `contrasena`) VALUES
(1, 'admin', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4'),
(2, 'maria', '88d4266fd4e6338d13b845fcf289579d209c897823b9217da3e161936f031589');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `followers`
--
ALTER TABLE `followers`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `repositorios`
--
ALTER TABLE `repositorios`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `followers`
--
ALTER TABLE `followers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `repositorios`
--
ALTER TABLE `repositorios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
